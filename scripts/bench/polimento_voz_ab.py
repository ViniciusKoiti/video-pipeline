"""Pares cegos de trechos de uma baseline, sem TTS nem escrita no episodio.

Exemplo: uv run python scripts/bench/polimento_voz_ab.py --episodio PASTA
  --baseline PASTA/renders/baseline-voz-2026-11-04/episode.json
  --trecho 8:12.5 --trecho 40.5:45 --saida data/benchmarks/voz-ab
O gabarito e as medidas ficam em privado/; ouvir index.html antes de abri-los.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.commands.errors import run  # noqa: E402
from app.media.constants.voice_level_constants import VoiceLevelConstants as C  # noqa: E402
from app.media.models.voice_level_report import VoiceLevelReport  # noqa: E402
from app.media.models.voice_polish import VoicePolish  # noqa: E402
from app.media.probe import duration_ms  # noqa: E402
from app.media.voice_level import VoiceLevelError, _ffmpeg, _measure, level_policy, level_voice  # noqa: E402
from app.pipeline.bench import cpu_probe  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_pair(
    episode: Path, scene: dict, begin: float, end: float, work: Path,
) -> tuple[list[dict], dict]:
    leveled = episode / scene['audio']
    record = VoiceLevelReport.model_validate_json(leveled.with_suffix('.json').read_text())
    raw = record.source.resolve()
    if not raw.is_relative_to((episode / 'voice').resolve()) or sha256(raw) != record.source_sha256:
        raise VoiceLevelError(f'{scene["id"]}: bruto fora da pasta ou diferente da baseline')
    if sha256(leveled) != record.wav_sha256 or record.policy != level_policy():
        raise VoiceLevelError(f'{scene["id"]}: copia da baseline alterada ou politica diferente')
    local = work / raw.name
    shutil.copyfile(raw, local)
    offset = scene['start_ms'] / 1000
    variants = []
    for name, polish in [('atual', None), ('polida', VoicePolish())]:
        full = level_voice(local, polish)
        if polish is None and sha256(full) != record.wav_sha256:
            raise VoiceLevelError(f'{scene["id"]}: reproducao v1 difere da copia da baseline')
        clip = work / f'{name}.wav'
        _ffmpeg(full, f'atrim=start={begin - offset:.6f}:end={end - offset:.6f},asetpts=PTS-STARTPTS',
                ['-c:a', 'pcm_s16le', str(clip)])
        variants.append({'name': name, 'clip': clip, 'policy': level_policy(polish),
                         'before': _measure(clip)})
    # Ganho constante, sem compressor/limiter adicional; alvo comum com folga de pico.
    target = min(C.TARGET_LUFS, *(v['before']['input_i'] + C.TRUE_PEAK_DBTP
                                - v['before']['input_tp'] - 0.1 for v in variants))
    for variant in variants:
        adjusted = work / f'{variant["name"]}-matched.wav'
        gain = target - variant['before']['input_i']
        _ffmpeg(variant['clip'], f'volume={gain:.6f}dB', ['-c:a', 'pcm_s16le', str(adjusted)])
        stats = _measure(adjusted)
        milliseconds = duration_ms(adjusted)
        if abs(stats['input_i'] - target) > 0.1 or stats['input_tp'] > C.TRUE_PEAK_DBTP:
            raise VoiceLevelError('par fora do volume ou pico combinado')
        if abs(milliseconds - round((end - begin) * 1000)) > C.DURATION_TOLERANCE_MS:
            raise VoiceLevelError('recorte com duracao diferente da planejada')
        variant.update(clip=adjusted, gain_db=gain, measured=stats, duration_ms=milliseconds)
    if abs(variants[0]['measured']['input_i'] - variants[1]['measured']['input_i']) > 0.1:
        raise VoiceLevelError('diferenca de volume entre A e B maior que 0,1 LU')
    return variants, {'scene': scene['id'], 'raw': str(raw), 'raw_sha256': sha256(raw),
                      'baseline_wav_sha256': record.wav_sha256, 'target_lufs': target}


def write_pair(out: Path, index: int, variants: list[dict]) -> list[dict]:
    secrets.SystemRandom().shuffle(variants)
    records = []
    for label, variant in zip(('A', 'B'), variants, strict=True):
        filename = f'par-{index:02d}-{label}.wav'
        destination = out / filename
        shutil.copyfile(variant['clip'], destination)
        records.append({**{k: v for k, v in variant.items() if k != 'clip'},
                        'label': label, 'file': filename, 'sha256': sha256(destination)})
    # Arquivo sequencial para uma critica cega: A, 1 segundo de silencio, B.
    joined = out / f'par-{index:02d}-A-pausa-B.wav'
    result = subprocess.run([
        'ffmpeg', '-v', 'error', '-nostdin', '-n', '-i', str(out / records[0]['file']),
        '-i', str(out / records[1]['file']), '-filter_complex',
        '[0:a]apad=pad_dur=1[a];[a][1:a]concat=n=2:v=0:a=1[out]',
        '-map', '[out]', '-c:a', 'pcm_s16le', str(joined),
    ], capture_output=True, text=True, check=False)
    if result.returncode:
        raise VoiceLevelError('falha ao juntar o par cego')
    return records


def page(windows: list[tuple[float, float]]) -> str:
    cards = []
    for index, (begin, end) in enumerate(windows, 1):
        players = ''.join(
            f'<p>{label}</p><audio controls preload="none" src="par-{index:02d}-{label}.wav"></audio>'
            for label in ('A', 'B')
        )
        cards.append(f'<section><h2>Par {index}: {begin:g} a {end:g} s do video</h2>{players}'
                     '<p>Preferencia: A / B / empate. Observe s/ch/x, clareza, abafamento e lingua presa.</p>'
                     '<textarea aria-label="Notas" placeholder="Anote a preferencia; este campo nao salva.">'
                     '</textarea></section>')
    return ('<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Escuta cega da voz</title><style>'
            'body{font:18px system-ui;background:#faf7f0;color:#252525;max-width:760px;'
            'margin:auto;padding:24px}section{border-top:1px solid #aaa;padding:20px 0}'
            'audio,textarea{width:100%}textarea{min-height:80px;box-sizing:border-box}'
            '</style><h1>Escuta cega da voz</h1><p>Dois tratamentos, mesmo volume por par. '
            'Use o mesmo fone e volume. A ordem foi sorteada independentemente em cada par. '
            'O gabarito esta separado em privado/. Nao abra antes de escolher.</p>'
            + ''.join(cards) + '</html>')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episodio', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--trecho', action='append', required=True, help='inicio:fim em segundos do video')
    parser.add_argument('--saida', type=Path, required=True)
    args = parser.parse_args()
    windows = [tuple(map(float, value.split(':'))) for value in args.trecho]
    if any(len(w) != 2 or not 0 <= w[0] < w[1] for w in windows):
        parser.error('cada trecho deve ter inicio:fim, com 0 <= inicio < fim')
    if args.saida.resolve().is_relative_to(args.episodio.resolve()):
        parser.error('a saida deve ficar fora do episodio')
    if args.saida.exists():
        parser.error('a saida ja existe; use uma pasta nova para preservar o teste')
    manifest = json.loads(args.baseline.read_text())
    selected = []
    for begin, end in windows:
        matches = [s for s in manifest['scenes'] if s['start_ms'] <= begin * 1000
                   and (s['start_ms'] + s['duration_ms']) >= end * 1000]
        if len(matches) != 1:
            parser.error('cada trecho deve ficar dentro de uma unica cena da baseline')
        selected.append(matches[0])
    probe = cpu_probe()
    if probe > 0.3:
        raise VoiceLevelError(f'maquina limitada: sonda {probe:.3f} s > 0,3 s')
    out = args.saida
    private = out / 'privado'
    private.mkdir(parents=True)
    private.chmod(0o700)
    key = {'baseline': str(args.baseline), 'baseline_sha256': sha256(args.baseline),
           'cpu_probe_s': probe, 'polish': VoicePolish().model_dump(), 'pairs': []}
    for index, ((begin, end), scene) in enumerate(zip(windows, selected, strict=True), 1):
        with tempfile.TemporaryDirectory(dir=private) as folder:
            variants, origin = prepare_pair(args.episodio, scene, begin, end, Path(folder))
            pair = {'index': index, 'start_s': begin, 'end_s': end, **origin,
                    'variants': write_pair(out, index, variants)}
            key['pairs'].append(pair)
        print(f'Par {index}: {begin:g}-{end:g} s; volume igualado, pico e duracao conferidos.')
    (private / 'gabarito.json').write_text(json.dumps(key, indent=2) + '\n')
    (out / 'index.html').write_text(page(windows))
    (out / 'respostas.txt').write_text(''.join(f'Par {i}: A / B / empate; observacoes:\n'
                                            for i in range(1, len(windows) + 1)))
    print(f'Escuta: {html.escape(str(out / "index.html"))}; gabarito separado em privado/.')


if __name__ == '__main__':
    raise SystemExit(run('polimento-voz-ab', main))
