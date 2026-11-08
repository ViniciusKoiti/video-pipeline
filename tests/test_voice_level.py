"""Volume por fala: FFmpeg real, bruto preservado, cache e integração com os dois formatos."""

from __future__ import annotations

import hashlib
import math
import wave
from array import array
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.media.constants.voice_level_constants import VoiceLevelConstants as C
from app.media.models.voice_level_report import VoiceLevelReport
from app.media.models.voice_polish import VoicePolish
from app.media.voice_level import VoiceLevelError, _ffmpeg, _measure, level_policy, level_voice
from app.media.voice_polish import polish_filters
from app.pipeline.models.naming import Naming
from app.pipeline.models.narration import Narration
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.models.status import Status
from app.pipeline.models.step import Step
from app.pipeline.short_voice import produce_short_voice, voice_entries
from app.pipeline.state import load_state
from app.pipeline.voice import Narrator, VoiceLibrary
from app.pipeline.voice_state import produce_with_state
from app.settings import load_settings
from app.settings.models.voice_polish_settings import VoicePolishSettings
from app.storage.json_files import JsonFileStore
from tests.fakes import FakeBatchTTS, wav_duration_ms
from tests.test_chatterbox_tts import FakeWorker, make_tts
from tests.test_voice_references import recordings


def tone(path: Path, amplitude: float) -> None:
    samples = array('h', (
        round(32767 * amplitude * math.sin(2 * math.pi * 440 * i / 24000)) for i in range(72000)
    ))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as wav:
        wav.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        wav.writeframes(samples.tobytes())


def report(path: Path) -> VoiceLevelReport:
    return VoiceLevelReport.model_validate_json(path.with_suffix('.json').read_text())


@pytest.mark.parametrize('polish', [None, VoicePolish()])
def test_quiet_and_loud_scenes_reach_the_same_level_and_keep_the_raw_audio(
    tmp_path: Path, polish: VoicePolish | None,
) -> None:
    originals = []
    levels = []
    for name, amplitude in [('quiet', 0.01), ('loud', 0.3)]:
        raw = tmp_path / f'{name}.wav'
        tone(raw, amplitude)
        before = raw.read_bytes()
        out = level_voice(raw, polish)
        measured = report(out)
        assert raw.read_bytes() == before and measured.source_sha256 == hashlib.sha256(before).hexdigest()
        assert abs(measured.output_lufs - C.TARGET_LUFS) <= C.TOLERANCE_LU
        assert measured.true_peak_dbtp <= C.TRUE_PEAK_DBTP + C.PEAK_TOLERANCE_DB
        with wave.open(str(out), 'rb') as wav:
            assert (wav.getnchannels(), wav.getframerate(), wav.getsampwidth()) == (2, 48000, 2)
        assert abs(wav_duration_ms(out) - wav_duration_ms(raw)) <= 20
        originals.append(measured.input_lufs)
        levels.append(measured.output_lufs)
    assert abs(originals[0] - originals[1]) > 20 and abs(levels[0] - levels[1]) < 0.5


def test_cache_reuses_only_intact_audio_and_changes_with_the_source_or_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = tmp_path / 'raw.wav'
    tone(raw, 0.05)
    first = level_voice(raw)
    before = first.stat().st_mtime_ns
    assert level_voice(raw) == first and first.stat().st_mtime_ns == before
    first.write_bytes(b'corrupted')
    assert level_voice(raw) == first and first.read_bytes()[:4] == b'RIFF'
    tone(raw, 0.1)
    second = level_voice(raw)
    assert second != first and first.is_file()
    monkeypatch.setattr(C, 'VERSION', 2)
    third = level_voice(raw)
    assert third not in (first, second) and first.is_file() and second.is_file()


@pytest.mark.parametrize('polish', [None, VoicePolish()])
def test_silence_is_pending_instead_of_being_amplified(
    tmp_path: Path, polish: VoicePolish | None,
) -> None:
    raw = tmp_path / 'silent.wav'
    tone(raw, 0)
    before = raw.read_bytes()
    with pytest.raises(VoiceLevelError, match='mensurável'):
        level_voice(raw, polish)
    assert raw.read_bytes() == before and not list((tmp_path / 'leveled').glob('*.wav'))


def test_level_failure_keeps_raw_speeches_and_retry_needs_no_new_tts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = JsonFileStore(tmp_path)
    voice = store.path('ep', 'voice')
    voice.mkdir(parents=True)
    tts = FakeBatchTTS()
    narrator = Narrator(tts, 'pt-BR', VoiceLibrary(voice, Naming.LONG), lambda p: wav_duration_ms(p) / 1000)
    lines = [SpeechLine('S01', 'Primeira.'), SpeechLine('S02', 'Segunda.')]

    def fail_one(path: Path, polish: VoicePolish | None = None) -> Path:
        if path.name.startswith('S01'):
            raise VoiceLevelError('nivelamento falhou')
        return path

    monkeypatch.setattr('app.pipeline.voice_state.level_voice', fail_one)
    outputs = produce_with_state(narrator, store, 'ep', lines, now=datetime.now(UTC), level=True)
    assert [o.status for o in outputs] == [Status.NEEDS_REVIEW, Status.COMPLETED]
    assert load_state(store, 'ep').get(Step.VOICE).scenes['S01'].reason == C.REASON
    assert len(list(voice.glob('*.wav'))) == 2
    calls = list(tts.calls)
    monkeypatch.setattr('app.pipeline.voice_state.level_voice', lambda path, polish=None: path)
    assert all(o.status is Status.COMPLETED for o in produce_with_state(
        narrator, store, 'ep', lines, now=datetime.now(UTC), level=True
    ))
    assert tts.calls == calls


class ToneWorker(FakeWorker):
    def ask(self, job: Mapping[str, Any]) -> dict[str, Any]:
        self.jobs.append(job)
        tone(Path(job['out_path']), 0.03)
        return {'ok': True}


@pytest.mark.parametrize('naming', [Naming.SHORT, Naming.LONG])
@pytest.mark.parametrize('polish', [None, VoicePolish()])
def test_production_paths_use_leveled_speech_and_keep_reference_and_level_records(
    tmp_path: Path, naming: Naming, monkeypatch: pytest.MonkeyPatch, polish: VoicePolish | None,
) -> None:
    refs = recordings(tmp_path / 'references')
    tts = make_tts(ToneWorker(), tmp_path, references=refs)
    store = JsonFileStore(tmp_path / 'episodes')
    folder = store.path('ep', '')
    folder.mkdir(parents=True)
    narration = Narration.model_validate({'language': 'pt-BR', 'lines': [
        {'scene': 'intro', 'text': 'Uma frase.', 'delivery': 'hook'},
    ]})
    if naming is Naming.SHORT:
        wavs = produce_short_voice(tts, narration, store, 'ep', polish=polish)
    else:
        from app.pipeline.voice_production import produce_voice
        from tests.test_voice_scripts import scenes

        manifest = scenes()
        wavs = list(produce_voice(tts, manifest, store, 'ep', polish=polish).values())
    assert wavs and all(w.parent.name == C.DIRECTORY for w in wavs)
    state = load_state(store, 'ep').get(Step.VOICE)
    assert all('/leveled/' in path for path in state.outputs)
    assert all(level_policy(polish) in record.detail for record in state.scenes.values())
    assert all(report(w).policy == level_policy(polish) for w in wavs)
    if naming is Naming.SHORT:
        monkeypatch.chdir(tmp_path)
        [entry] = voice_entries(narration, wavs, lambda _: (0.0, 3.0), tts, folder.relative_to(tmp_path))
        assert entry['wav'].startswith('voice/leveled/')
        assert entry['level']['source'].endswith('.wav') and entry['reference']['sha256']


def test_none_reproduces_legacy_bytes_policy_and_filename(tmp_path: Path) -> None:
    raw, legacy = tmp_path / 'raw.wav', tmp_path / 'legacy.wav'
    tone(raw, 0.05)
    measured = _measure(raw, mono=True)
    _ffmpeg(raw, (
        f'aformat=channel_layouts=mono,pan=stereo|c0=c0|c1=c0,loudnorm=I={C.TARGET_LUFS}:'
        f'TP={C.TRUE_PEAK_DBTP}:LRA={C.LRA}:measured_I={measured["input_i"]}:'
        f'measured_TP={measured["input_tp"]}:measured_LRA={measured["input_lra"]}:'
        f'measured_thresh={measured["input_thresh"]}:offset={measured["target_offset"]}:linear=true,'
        f'aresample={C.SAMPLE_RATE}'
    ), ['-c:a', 'pcm_s16le', str(legacy)])
    out = level_voice(raw, None)
    policy = 'loudnorm-v1:-16.0:-1.5:11:48000'
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    key = hashlib.sha256(f'{digest}|{policy}'.encode()).hexdigest()[:12]
    assert out.name == f'raw-{key}.wav' and report(out).policy == policy
    assert out.read_bytes() == legacy.read_bytes()
    before = out.stat().st_mtime_ns
    assert level_voice(raw) == out and out.stat().st_mtime_ns == before


def test_polish_cache_is_separate_and_tracks_effective_parameters(tmp_path: Path) -> None:
    raw = tmp_path / 'raw.wav'
    tone(raw, 0.05)
    original = raw.read_bytes()
    plain = level_voice(raw)
    unchanged = plain.read_bytes(), plain.stat().st_mtime_ns
    polish = VoicePolish()
    first = level_voice(raw, polish)
    timestamp = first.stat().st_mtime_ns
    assert level_voice(raw, polish) == first and first.stat().st_mtime_ns == timestamp
    changed = level_voice(raw, VoicePolish(deesser_intensity=0.2))
    assert len({plain, first, changed}) == 3
    first.write_bytes(b'corrupted')
    assert level_voice(raw, polish) == first and first.read_bytes()[:4] == b'RIFF'
    assert level_voice(raw) == plain
    assert (plain.read_bytes(), plain.stat().st_mtime_ns) == unchanged and raw.read_bytes() == original
    assert ':polish-v2:' in report(first).policy
    assert level_policy(VoicePolish(eq_hz=4000)) == level_policy(polish)  # EQ desligado
    assert level_policy(VoicePolish(eq_gain_db=-1)) != level_policy(polish)


def band_amplitude(path: Path, hz: int) -> float:
    with wave.open(str(path), 'rb') as wav:
        rate, channels = wav.getframerate(), wav.getnchannels()
        samples = array('h', wav.readframes(wav.getnframes()))[::channels]
    samples = samples[rate:2 * rate]  # descarta os transientes do filtro
    real = sum(v * math.cos(2 * math.pi * hz * i / rate) for i, v in enumerate(samples))
    imag = sum(v * math.sin(2 * math.pi * hz * i / rate) for i, v in enumerate(samples))
    return math.hypot(real, imag) / len(samples)


def test_polish_reduces_sibilant_band_without_removing_body(tmp_path: Path) -> None:
    raw, out = tmp_path / 'sibilant.wav', tmp_path / 'filtered.wav'
    samples = array('h', (
        round(32767 * (0.1 * math.sin(2 * math.pi * 440 * i / 24000)
                       + 0.2 * math.sin(2 * math.pi * 7000 * i / 24000))) for i in range(72000)
    ))
    with wave.open(str(raw), 'wb') as wav:
        wav.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        wav.writeframes(samples.tobytes())
    # Isola a cadeia: o loudnorm compensa o ganho global e mascararia a medicao por banda.
    _ffmpeg(raw, polish_filters(VoicePolish()).rstrip(','), ['-c:a', 'pcm_s16le', str(out)])
    assert band_amplitude(out, 7000) < band_amplitude(raw, 7000) * 0.95
    assert band_amplitude(out, 440) == pytest.approx(band_amplitude(raw, 440), rel=0.03)
    leveled = level_voice(raw, VoicePolish())
    assert abs(report(leveled).output_lufs - C.TARGET_LUFS) <= C.TOLERANCE_LU
    assert report(leveled).true_peak_dbtp <= C.TRUE_PEAK_DBTP + C.PEAK_TOLERANCE_DB
    assert abs(wav_duration_ms(leveled) - wav_duration_ms(raw)) <= C.DURATION_TOLERANCE_MS


def test_polish_settings_are_opt_in_and_eq_is_omitted_by_default() -> None:
    settings = load_settings(Path(__file__).resolve().parents[1], environ={})
    assert settings.voice_polish.active() is None
    assert VoicePolishSettings().active() is None
    polish = VoicePolishSettings(enabled=True).active()
    assert polish == VoicePolish() and polish_filters(None) == ''
    assert 'equalizer=' not in polish_filters(polish)
    assert 'equalizer=' in polish_filters(VoicePolish(eq_gain_db=-1))


def test_both_passes_polish_but_output_validation_does_not_reapply_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.media import voice_level

    raw = tmp_path / 'raw.wav'
    tone(raw, 0.05)
    calls = []

    def capture(source: Path, filters: str, output: list[str]) -> str:
        calls.append((source, filters))
        return _ffmpeg(source, filters, output)

    monkeypatch.setattr(voice_level, '_ffmpeg', capture)
    polish = VoicePolish(eq_gain_db=-1)
    level_voice(raw, polish)
    assert len(calls) == 3
    for source, filters in calls[:2]:
        assert source == raw and filters.count(polish_filters(polish)) == 1
        assert filters.index('highpass=') < filters.index('equalizer=')
        assert filters.index('equalizer=') < filters.index('deesser=') < filters.index('loudnorm=')
    assert calls[2][0] != raw and 'deesser=' not in calls[2][1]


def test_policy_change_updates_state_without_new_synthesis(tmp_path: Path) -> None:
    store = JsonFileStore(tmp_path)
    voice = store.path('ep', 'voice')
    voice.mkdir(parents=True)
    worker = ToneWorker()
    tts = make_tts(worker, tmp_path)
    narrator = Narrator(tts, 'pt-BR', VoiceLibrary(voice, Naming.LONG), lambda p: wav_duration_ms(p) / 1000)
    lines = [SpeechLine('S01', 'Uma frase.')]
    states, paths = [], []
    for polish in (None, VoicePolish(), None):
        [outcome] = produce_with_state(
            narrator, store, 'ep', lines, now=datetime.now(UTC), level=True, polish=polish,
        )
        assert outcome.status is Status.COMPLETED
        assert level_policy(polish) in outcome.detail
        paths.append(outcome.value)
        states.append(load_state(store, 'ep').get(Step.VOICE).input_hash)
    assert states[0] == states[2] != states[1] and paths[0] == paths[2] != paths[1]
    assert len(worker.jobs) == 1


@pytest.mark.parametrize(('field', 'value'), [
    ('highpass_hz', 0), ('deesser_intensity', -0.1), ('deesser_max', 1.1),
    ('deesser_frequency', float('nan')), ('eq_gain_db', float('inf')), ('eq_width_octaves', 0),
])
def test_invalid_polish_parameters_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ValidationError):
        VoicePolish.model_validate({field: value})
