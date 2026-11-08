"""Timer do benchmark: rede sempre falsa, orcamento finito e nenhum reenvio apos sucesso."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from scripts.bench import earshot_retry as retry


@pytest.fixture
def job(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / 'comparacao-A-pausa-B.wav').write_bytes(b'fake-local-audio')
    monkeypatch.setattr(retry, 'cpu_probe', lambda: 0.05)
    return tmp_path


def test_success_stops_and_never_calls_again(job: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def attempt(media, output, comparison):
        calls.append(media)
        return {'ok': True, 'critique': {'answer': 'Empate; diferenca inconclusiva.'}}

    monkeypatch.setattr(retry, 'attempt', attempt)
    state = retry.tick(job, now=1000)
    assert state['status'] == 'completed' and state['attempts'] == 1
    assert retry.tick(job, now=2000) == state
    assert len(calls) == 1


@pytest.mark.parametrize('code', [500, 502, 503, 504])
def test_transient_failure_waits_and_has_a_hard_call_limit(
    job: Path, monkeypatch: pytest.MonkeyPatch, code: int,
) -> None:
    calls = []

    def attempt(media, output, comparison):
        calls.append(media)
        return {'ok': False, 'error': f'Gemini HTTP {code}: unavailable'}

    monkeypatch.setattr(retry, 'attempt', attempt)
    clock = 1000.0
    monkeypatch.setattr(retry.time, 'time', lambda: clock)
    first = retry.tick(job)
    assert first['status'] == 'waiting' and first['next_at'] == 1300
    assert retry.tick(job, now=1299)['attempts'] == 1
    for _ in range(5):
        clock += 300
        state = retry.tick(job)
    assert state['status'] == 'exhausted' and state['attempts'] == 6
    assert retry.tick(job, now=4000)['status'] == 'exhausted'
    assert len(calls) == 6
    assert len(list((job / 'retentativas').glob('tentativa-*.json'))) == 6


@pytest.mark.parametrize('error', [
    'Gemini HTTP 429: quota exhausted', 'Gemini HTTP 401: rejected',
    'Gemini HTTP 403: forbidden', 'Gemini HTTP 404: model not found',
    'Timeout local; resultado remoto desconhecido.', 'network error talking to Gemini',
])
def test_permanent_or_uncertain_failure_does_not_retry(
    job: Path, monkeypatch: pytest.MonkeyPatch, error: str,
) -> None:
    calls = []
    monkeypatch.setattr(retry, 'attempt', lambda *args: calls.append(args) or {'ok': False, 'error': error})
    assert retry.tick(job, now=1000)['status'] == 'failed'
    assert retry.tick(job, now=2000)['status'] == 'failed'
    assert len(calls) == 1


def test_busy_cpu_sends_nothing_and_expires(job: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(retry, 'cpu_probe', lambda: 0.5)
    monkeypatch.setattr(retry, 'attempt', lambda *args: pytest.fail('nao deveria enviar audio'))
    state = retry.tick(job, now=1000)
    assert state['attempts'] == 0 and state['status'] == 'waiting'
    assert retry.tick(job, now=8200)['status'] == 'expired'


def test_interrupted_request_and_changed_input_are_not_repeated(
    job: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(retry, 'cpu_probe', lambda: 0.5)
    retry.tick(job, now=1000)
    path = job / 'retentativas' / 'estado.json'
    state = json.loads(path.read_text())
    state.update(status='running', attempts=1)
    retry.save(path, state)
    monkeypatch.setattr(retry, 'attempt', lambda *args: pytest.fail('nao deveria repetir'))
    assert retry.tick(job, now=2000)['status'] == 'interrupted'
    state.update(status='waiting', next_at=1300)
    retry.save(path, state)
    (job / 'comparacao-A-pausa-B.wav').write_bytes(b'changed')
    assert retry.tick(job, now=2000)['status'] == 'failed'


def test_empty_critique_is_not_a_valid_comparative_answer() -> None:
    assert retry.classify({'ok': True, 'critique': {}}) == 'failed'
    assert retry.classify({'ok': True, 'critique': {'answer': '  '}}) == 'failed'


def test_authorized_extension_keeps_history_and_does_not_reset_on_each_tick(
    job: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(retry, 'cpu_probe', lambda: 0.5)
    retry.tick(job, now=1000)
    path = job / 'retentativas' / 'estado.json'
    state = json.loads(path.read_text())
    state.update(status='exhausted', attempts=6)
    retry.save(path, state)
    extended = retry.tick(job, now=9000, extend_to=12)
    assert extended['status'] == 'waiting' and extended['attempts'] == 6
    assert extended['max_attempts'] == 12 and extended['deadline'] == 16200
    assert len(extended['extensions']) == 1
    assert extended['extensions'][0]['attempts_kept'] == 6
    assert retry.tick(job, now=9001, extend_to=12)['deadline'] == 16200
    monkeypatch.setattr(retry, 'cpu_probe', lambda: 0.05)
    monkeypatch.setattr(retry, 'attempt', lambda *args: {'ok': False, 'error': 'Gemini HTTP 503: busy'})
    monkeypatch.setattr(retry.time, 'time', lambda: 9300)
    state = retry.tick(job, extend_to=12)
    assert state['attempts'] == 7 and state['max_attempts'] == 12
    assert Path(state['result']).name == 'tentativa-07.json'


@pytest.mark.parametrize('status', ['completed', 'failed', 'interrupted'])
def test_extension_cannot_reopen_success_permanent_error_or_unknown_result(
    job: Path, monkeypatch: pytest.MonkeyPatch, status: str,
) -> None:
    monkeypatch.setattr(retry, 'cpu_probe', lambda: 0.5)
    retry.tick(job, now=1000)
    path = job / 'retentativas' / 'estado.json'
    state = json.loads(path.read_text())
    state.update(status=status)
    retry.save(path, state)
    monkeypatch.setattr(retry, 'attempt', lambda *args: pytest.fail('nao deveria enviar'))
    assert retry.tick(job, now=9000, extend_to=12) == state


def test_short_comparison_uses_its_duration_and_five_call_budget(
    job: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = {'duration_s': 12.92, 'lufs': -16.0, 'max_attempts': 5}
    (job / 'comparacao.json').write_text(json.dumps(config))
    received = []
    monkeypatch.setattr(retry, 'attempt', lambda media, output, comparison:
                        received.append(comparison) or {'ok': False, 'error': 'Gemini HTTP 503: busy'})
    clock = 1000
    monkeypatch.setattr(retry.time, 'time', lambda: clock)
    for _ in range(5):
        state = retry.tick(job)
        clock += 300
    assert state['status'] == 'exhausted' and state['attempts'] == state['max_attempts'] == 5
    assert received == [config] * 5
    retry.tick(job)
    assert len(received) == 5


def test_changed_comparison_settings_do_not_send_another_request(
    job: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = {'duration_s': 12.92, 'lufs': -16.0, 'max_attempts': 5}
    path = job / 'comparacao.json'
    path.write_text(json.dumps(config))
    monkeypatch.setattr(retry, 'cpu_probe', lambda: 0.5)
    retry.tick(job, now=1000)
    path.write_text(json.dumps({**config, 'duration_s': 13}))
    monkeypatch.setattr(retry, 'attempt', lambda *args: pytest.fail('nao deveria enviar'))
    assert retry.tick(job, now=2000)['status'] == 'failed'


@pytest.mark.parametrize('change', [
    {'duration_s': float('nan')}, {'duration_s': 0}, {'max_attempts': 25},
    {'max_attempts': True}, {'lufs': float('inf')}, {'unexpected': 1},
])
def test_invalid_short_comparison_settings_are_rejected(job: Path, change: dict) -> None:
    config = {'duration_s': 12.92, 'lufs': -16.0, 'max_attempts': 5}
    (job / 'comparacao.json').write_text(json.dumps({**config, **change}))
    with pytest.raises(retry.RetryError):
        retry.tick(job, now=1000)


def test_earshot_request_has_short_boundaries_and_never_puts_key_in_command(
    job: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    key = 'fake-test-secret'
    settings = SimpleNamespace(earshot=SimpleNamespace(python=Path('/fake/python')),
                               secrets=SimpleNamespace(gemini_api_key=SecretStr(key)))
    monkeypatch.setattr(retry, 'load_settings', lambda _: settings)
    output = job / 'response.json'
    commands = []

    def launch(command, **kwargs):
        commands.append(command)
        assert kwargs['env']['GEMINI_API_KEY'] == key
        output.write_text(json.dumps({'ok': True, 'critique': {'answer': 'Empate'}, 'extra': key}))

    monkeypatch.setattr(retry.subprocess, 'run', launch)
    result = retry.attempt(job / 'comparacao-A-pausa-B.wav', output,
                           {'duration_s': 12.92, 'lufs': -16.0, 'max_attempts': 5})
    [command] = commands
    assert command[command.index('--max-seconds') + 1] == '26.84'
    prompt = command[command.index('--prompt') + 1]
    assert '12.92' in prompt and '13.92' in prompt and '26.84' in prompt
    assert '45,64' not in prompt and '92,28' not in prompt and key not in ' '.join(command)
    assert result['extra'] == '[REDACTED]' and key not in output.read_text()
