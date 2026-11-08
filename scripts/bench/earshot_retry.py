"""Uma tentativa de critica por disparo do timer; sem retry interno nem fallback pago.

Estado e respostas ficam em <pasta>/retentativas/. Sucesso, erro permanente,
6 chamadas (ampliaveis por autorizacao) ou prazo de 2 horas encerram o timer. Uma execucao interrompida nao
repete uma requisicao de resultado desconhecido.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.commands.errors import run  # noqa: E402
from app.errors import PipelineError  # noqa: E402
from app.pipeline.bench import cpu_probe  # noqa: E402
from app.settings import load_settings  # noqa: E402

MAX_ATTEMPTS = 6
INTERVAL_S = 300
DEADLINE_S = 7200
MODEL = 'gemini-3.8-flash'
TERMINAL = frozenset({'completed', 'failed', 'exhausted', 'expired', 'interrupted'})
PROMPT = (
    'Responda em portugues do Brasil. Compare duas versoes da MESMA narracao pt-BR. '
    'A toca de 0 a {duration:g} s, depois ha 1 s de silencio; '
    'B toca de {second_start:g} a {total:g} s. '
    'Ambas tem volume integrado {lufs:g} LUFS, duracao {duration:g} s cada, pico abaixo de -1,5 dBTP '
    'e diferenca de volume menor que 0,1 LU. Nao sabe qual tratamento recebeu cada uma. '
    'A voz clonada e intencional e nao e um defeito por si so. E um ensaio narrado, nao anuncio. '
    'Sem imagem, efeitos ou musica: sincronia e musica devem ser nulas. '
    'Compare sibilancia em s/ch/x, conforto, clareza, prosodia, corpo, brilho, abafamento, '
    'lingua presa e artefatos. Avalie tambem pronuncia de nomes e termos estrangeiros, '
    'sem presumir erros. Ignore silencio de preenchimento no fim dos recortes e a pausa '
    'separadora; julgue a fala. Nao presuma melhoria. Se forem indistinguiveis, diga empate '
    'ou inconclusivo. No campo answer, de uma nota perceptual de 1 a 10 para CADA versao, '
    'informe preferencia A/B/empate/inconclusivo e confianca, justificando somente diferencas '
    'audiveis especificas. Nao busque uma nota desejada. Separe observacao de hipotese. '
    'Nao invente frequencias ou medidas. Diga se a diferenca sustenta alterar a producao. '
    'A copia enviada e MP3 mono 64 kbps: explicite a limitacao para sutilezas dos agudos. '
    'Notas sao opiniao de LLM, nao MOS validado. Tempos de defeitos sao aproximados.'
)


class RetryError(PipelineError, RuntimeError):
    pass


def save(path: Path, state: dict) -> None:
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def classify(result: dict) -> str:
    critique = result.get('critique')
    answer = critique.get('answer') if isinstance(critique, dict) else None
    if result.get('ok') is True and isinstance(answer, str) and answer.strip():
        return 'completed'
    error = str(result.get('error') or result.get('summary') or '')
    return 'waiting' if re.search(r'Gemini HTTP (500|502|503|504)\b', error) else 'failed'


def comparison_config(folder: Path) -> dict:
    path = folder / 'comparacao.json'
    config = json.loads(path.read_text()) if path.exists() else {
        'duration_s': 45.64, 'lufs': -16.16, 'max_attempts': MAX_ATTEMPTS,
    }
    if set(config) != {'duration_s', 'lufs', 'max_attempts'}:
        raise RetryError('campos invalidos em comparacao.json')
    duration, lufs, limit = config['duration_s'], config['lufs'], config['max_attempts']
    if (not isinstance(duration, (int, float)) or isinstance(duration, bool)
            or not math.isfinite(duration) or not 0 < duration <= 60):
        raise RetryError('duracao por versao invalida')
    if (not isinstance(lufs, (int, float)) or isinstance(lufs, bool)
            or not math.isfinite(lufs) or not -30 <= lufs <= -10):
        raise RetryError('loudness invalida')
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 24:
        raise RetryError('limite de tentativas invalido')
    return config


def attempt(media: Path, output: Path, comparison: dict) -> dict:
    settings = load_settings(ROOT)
    python = settings.earshot.python
    key = settings.secrets.gemini_api_key
    if python is None or key is None:
        return {'ok': False, 'error': 'EARSHOT_PYTHON ou GEMINI_API_KEY ausente'}
    env = dict(os.environ)
    env.update(GEMINI_API_KEY=key.get_secret_value(), EARSHOT_OFFLINE='1', EARSHOT_THREADS='3')
    child = 'from earshot import llm; llm.RETRY_WAIT = (); from earshot.cli import main; '
    child += 'raise SystemExit(main())'
    duration = comparison['duration_s']
    total = 2 * duration + 1
    prompt = PROMPT.format(duration=duration, second_start=duration + 1,
                           total=total, lufs=comparison['lufs'])
    command = [str(python.expanduser()), '-c', child, 'llm', str(media), '--yes-upload',
               '--model', MODEL, '--max-seconds', str(total), '--no-cuts', '--synth-intended',
               '--prompt', prompt, '--out', str(output)]
    try:
        subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True,
                       timeout=660, check=False)
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'Timeout local; resultado remoto desconhecido. Nao repetir.'}
    if not output.is_file():
        return {'ok': False, 'error': 'earshot terminou sem relatorio. Nao repetir automaticamente.'}
    # O earshot ja oculta a chave; mantem a mesma protecao antes de persistir qualquer resposta.
    safe = output.read_text().replace(key.get_secret_value(), '[REDACTED]')
    output.write_text(safe)
    return json.loads(safe)


def tick(folder: Path, now: float | None = None, extend_to: int | None = None) -> dict:
    now = time.time() if now is None else now
    if extend_to is not None and not 1 <= extend_to <= 24:
        raise RetryError('limite total deve estar entre 1 e 24')
    media = folder / 'comparacao-A-pausa-B.wav'
    if not media.is_file():
        raise RetryError('arquivo de comparacao ausente')
    comparison = comparison_config(folder)
    directory = folder / 'retentativas'
    directory.mkdir(exist_ok=True)
    directory.chmod(0o700)
    with (directory / '.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {'status': 'busy', 'attempts': 0}
        path = directory / 'estado.json'
        digest = hashlib.sha256(media.read_bytes()).hexdigest()
        state = json.loads(path.read_text()) if path.exists() else {
            'status': 'waiting', 'attempts': 0, 'created_at': now, 'deadline': now + DEADLINE_S,
            'next_at': now, 'media_sha256': digest, 'model': MODEL,
            'max_attempts': comparison['max_attempts'], 'interval_s': INTERVAL_S,
            'comparison': comparison,
        }
        if (extend_to is not None and extend_to > state['max_attempts']
                and state['status'] in {'waiting', 'exhausted', 'expired'}):
            state.setdefault('extensions', []).append({
                'at': now, 'previous_limit': state['max_attempts'], 'new_limit': extend_to,
                'attempts_kept': state['attempts'], 'previous_deadline': state['deadline'],
            })
            state.update(status='waiting', max_attempts=extend_to,
                         next_at=now, deadline=now + DEADLINE_S)
        if state['status'] in TERMINAL:
            return state
        if state['status'] == 'running':
            state.update(status='interrupted', reason='Resultado anterior desconhecido; nao repetir.')
        elif state['media_sha256'] != digest:
            state.update(status='failed', reason='Arquivo mudou; exige novo teste autorizado.')
        elif state.get('comparison', comparison) != comparison:
            state.update(status='failed', reason='Configuracao mudou; exige novo teste autorizado.')
        elif now >= state['deadline']:
            state.update(status='expired')
        elif state['attempts'] >= state['max_attempts']:
            state.update(status='exhausted')
        elif now < state['next_at']:
            return state
        else:
            probe = cpu_probe()
            state['cpu_probe_s'] = probe
            if probe > 0.3:
                state.update(next_at=now + INTERVAL_S, reason='CPU limitada; nenhuma chamada enviada.')
            else:
                state.update(status='running', attempts=state['attempts'] + 1, last_attempt_at=now)
                save(path, state)  # reserva a tentativa antes do envio
                output = directory / f'tentativa-{state["attempts"]:02d}.json'
                if output.exists():
                    state.update(status='interrupted', reason='Resposta ja existe; nao repetir.')
                else:
                    result = attempt(media, output, comparison)
                    if not output.exists():
                        save(output, result)
                    status = classify(result)
                    if status == 'waiting' and state['attempts'] >= state['max_attempts']:
                        status = 'exhausted'
                    state.update(status=status, result=str(output), updated_at=time.time(),
                                 next_at=time.time() + INTERVAL_S)
                    state['reason'] = str(result.get('error') or result.get('summary') or '')
        save(path, state)
        return state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pasta', type=Path, required=True)
    parser.add_argument('--timer-unit', help='timer transitorio desta avaliacao, para parar ao terminar')
    parser.add_argument('--ampliar-para', type=int,
                        help='novo limite TOTAL autorizado; preserva chamadas anteriores')
    args = parser.parse_args()
    if args.timer_unit and not re.fullmatch(r'earshot-voz-[a-z0-9-]+\.timer', args.timer_unit):
        parser.error('nome de timer invalido')
    state = tick(args.pasta.resolve(), extend_to=args.ampliar_para)
    limit = state.get('max_attempts', MAX_ATTEMPTS)
    print(f'earshot: {state["status"]}; {state["attempts"]}/{limit} tentativa(s)')
    if state['status'] in TERMINAL and args.timer_unit:
        subprocess.run(['systemctl', '--user', 'stop', args.timer_unit],
                       capture_output=True, text=True, timeout=15, check=False)


if __name__ == '__main__':
    raise SystemExit(run('earshot-retry', main))
