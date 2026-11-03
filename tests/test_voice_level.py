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

from app.media.constants.voice_level_constants import VoiceLevelConstants as C
from app.media.models.voice_level_report import VoiceLevelReport
from app.media.voice_level import VoiceLevelError, level_policy, level_voice
from app.pipeline.models.naming import Naming
from app.pipeline.models.narration import Narration
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.models.status import Status
from app.pipeline.models.step import Step
from app.pipeline.short_voice import produce_short_voice, voice_entries
from app.pipeline.state import load_state
from app.pipeline.voice import Narrator, VoiceLibrary
from app.pipeline.voice_state import produce_with_state
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


def test_quiet_and_loud_scenes_reach_the_same_level_and_keep_the_raw_audio(tmp_path: Path) -> None:
    originals = []
    levels = []
    for name, amplitude in [('quiet', 0.01), ('loud', 0.3)]:
        raw = tmp_path / f'{name}.wav'
        tone(raw, amplitude)
        before = raw.read_bytes()
        out = level_voice(raw)
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


def test_silence_is_pending_instead_of_being_amplified(tmp_path: Path) -> None:
    raw = tmp_path / 'silent.wav'
    tone(raw, 0)
    before = raw.read_bytes()
    with pytest.raises(VoiceLevelError, match='mensurável'):
        level_voice(raw)
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

    def fail_one(path: Path) -> Path:
        if path.name.startswith('S01'):
            raise VoiceLevelError('nivelamento falhou')
        return path

    monkeypatch.setattr('app.pipeline.voice_state.level_voice', fail_one)
    outputs = produce_with_state(narrator, store, 'ep', lines, now=datetime.now(UTC), level=True)
    assert [o.status for o in outputs] == [Status.NEEDS_REVIEW, Status.COMPLETED]
    assert load_state(store, 'ep').get(Step.VOICE).scenes['S01'].reason == C.REASON
    assert len(list(voice.glob('*.wav'))) == 2
    calls = list(tts.calls)
    monkeypatch.setattr('app.pipeline.voice_state.level_voice', lambda path: path)
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
def test_production_paths_use_leveled_speech_and_keep_reference_and_level_records(
    tmp_path: Path, naming: Naming, monkeypatch: pytest.MonkeyPatch
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
        wavs = produce_short_voice(tts, narration, store, 'ep')
    else:
        from app.pipeline.voice_production import produce_voice
        from tests.test_voice_scripts import scenes

        manifest = scenes()
        wavs = list(produce_voice(tts, manifest, store, 'ep').values())
    assert wavs and all(w.parent.name == C.DIRECTORY for w in wavs)
    state = load_state(store, 'ep').get(Step.VOICE)
    assert all('/leveled/' in path for path in state.outputs)
    assert all(level_policy() in record.detail for record in state.scenes.values())
    if naming is Naming.SHORT:
        monkeypatch.chdir(tmp_path)
        [entry] = voice_entries(narration, wavs, lambda _: (0.0, 3.0), tts, folder.relative_to(tmp_path))
        assert entry['wav'].startswith('voice/leveled/')
        assert entry['level']['source'].endswith('.wav') and entry['reference']['sha256']
