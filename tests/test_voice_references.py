"""Referência por idioma/cena: seleção, cache, estado e metadados sem voz real nem rede."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.bootstrap import LazyContext
from app.pipeline.models.naming import Naming
from app.pipeline.models.narration import Narration
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.models.status import Status
from app.pipeline.models.step import Step
from app.pipeline.short_voice import voice_entries
from app.pipeline.state import load_state
from app.pipeline.voice import Narrator, VoiceLibrary
from app.pipeline.voice_state import produce_with_state
from app.providers.errors import ModelUnavailable
from app.providers.tts.base import SpeechRequest
from app.providers.tts.chatterbox import reference_hash
from app.settings.models.chatterbox_settings import ChatterboxSettings
from app.storage.json_files import JsonFileStore
from tests.fakes import make_settings, wav_duration_ms
from tests.test_chatterbox_tts import FakeWorker, make_tts, write_wav

TONES = ("hook", "turn", "invite", "neutral", "calm")


def recordings(folder: Path) -> dict[str, dict[str, Path]]:
    result = {}
    for language in ("pt-BR", "en"):
        result[language] = {}
        for i, tone in enumerate(TONES):
            path = folder / language / f"{tone}.wav"
            path.parent.mkdir(parents=True, exist_ok=True)
            write_wav(path, 100 + i + (language == "en") * 100)
            result[language][tone] = path
    return result


@pytest.mark.parametrize("language", ["pt-BR", "en"])
@pytest.mark.parametrize("delivery", TONES)
def test_the_same_reference_is_used_for_selection_cache_and_synthesis(
    tmp_path: Path, language: str, delivery: str
) -> None:
    refs = recordings(tmp_path / "references")
    worker = FakeWorker()
    tts = make_tts(worker, tmp_path, references=refs)
    request = SpeechRequest("Uma frase.", tmp_path / "out.wav", language=language, delivery=delivery)
    expected = refs[language][delivery]
    selection = tts.reference_for(request)
    assert selection.path == expected and tts.scene_references
    assert selection.remote_name == f"references/{language}/{delivery}.wav"
    assert reference_hash(expected) in tts.fingerprint(request)
    result = tts.synthesize_speech(request)
    assert worker.jobs[0]["reference"] == str(expected)
    assert worker.jobs[0]["reference_name"] == selection.remote_name
    assert result.voice == f"clone:{reference_hash(expected)}"


def test_unmapped_uses_the_original_but_missing_or_invalid_mapped_wav_never_does(tmp_path: Path) -> None:
    refs = recordings(tmp_path / "references")
    worker = FakeWorker()
    tts = make_tts(worker, tmp_path, references={"pt-BR": {"hook": refs["pt-BR"]["hook"]}})
    req = SpeechRequest("Olá.", tmp_path / "out.wav", language="pt-BR")
    assert tts.reference_for(req).path == tmp_path / "voz.wav"
    assert tts.reference_for(replace(req, delivery="hook")).path == refs["pt-BR"]["hook"]
    for invalid in (None, b"invalid wav"):
        path = refs["pt-BR"]["hook"]
        if invalid is None:
            path.unlink()
        else:
            path.write_bytes(invalid)
        for operation in (tts.fingerprint, tts.synthesize_speech):
            with pytest.raises(ModelUnavailable, match="pt-BR/hook"):
                operation(replace(req, delivery="hook"))
    assert worker.jobs == []


@pytest.mark.parametrize("naming", [Naming.SHORT, Naming.LONG])
def test_changing_one_reference_regenerates_only_its_scenes_and_records_the_identity(
    tmp_path: Path, naming: Naming
) -> None:
    refs = recordings(tmp_path / "references")
    store = JsonFileStore(tmp_path / "episodes")
    voice = store.path("test", "voice")
    voice.mkdir(parents=True)
    worker = FakeWorker()
    tts = make_tts(worker, tmp_path, references=refs)
    narrator = Narrator(tts, "pt-BR", VoiceLibrary(voice, naming), lambda p: wav_duration_ms(p) / 1000)
    lines = [SpeechLine("intro", "Uma frase.", "hook"), SpeechLine("explain", "Outra frase.", "calm")]
    now = datetime(2026, 11, 1, tzinfo=UTC)
    first = produce_with_state(narrator, store, "test", lines, now=now)
    old_key = load_state(store, "test").get(Step.VOICE).input_hash
    assert len(worker.jobs) == 2
    produce_with_state(narrator, store, "test", lines, now=now)
    assert len(worker.jobs) == 2  # retomada é só cache
    write_wav(refs["pt-BR"]["hook"], 500)
    second = produce_with_state(narrator, store, "test", lines, now=now)
    assert len(worker.jobs) == 3
    assert second[0].value != first[0].value and second[1].value == first[1].value
    state = load_state(store, "test").get(Step.VOICE)
    assert state.input_hash != old_key and state.status is Status.COMPLETED
    assert reference_hash(refs["pt-BR"]["hook"]) in state.scenes["intro"].detail
    assert "entrega:hook=0.8,0.3" in state.scenes["intro"].detail
    assert reference_hash(refs["pt-BR"]["calm"]) in state.scenes["explain"].detail


def test_missing_reference_is_a_scene_pending_and_does_not_stop_other_scenes(tmp_path: Path) -> None:
    refs = recordings(tmp_path / "references")
    refs["pt-BR"]["hook"].unlink()
    store = JsonFileStore(tmp_path / "episodes")
    voice = store.path("test", "voice")
    voice.mkdir(parents=True)
    worker = FakeWorker()
    tts = make_tts(worker, tmp_path, references=refs)
    narrator = Narrator(tts, "pt-BR", VoiceLibrary(voice, Naming.SHORT), lambda p: wav_duration_ms(p) / 1000)
    lines = [SpeechLine("intro", "Uma frase.", "hook"), SpeechLine("explain", "Outra frase.", "calm")]
    outcomes = produce_with_state(narrator, store, "test", lines, now=datetime.now(UTC))
    assert [o.status for o in outcomes] == [Status.NEEDS_REVIEW, Status.COMPLETED]
    state = load_state(store, "test").get(Step.VOICE)
    assert state.pending_scenes == ["intro"] and state.scenes["intro"].reason == "model_unavailable"
    assert len(worker.jobs) == 1
    write_wav(refs["pt-BR"]["hook"], 800)
    assert all(o.status is Status.COMPLETED for o in narrator.produce(lines))
    assert len(worker.jobs) == 2


def test_short_voice_record_identifies_the_reference_even_when_wavs_are_reused(tmp_path: Path) -> None:
    refs = recordings(tmp_path / "references")
    tts = make_tts(folder=tmp_path, references=refs)
    narration = Narration.model_validate({"language": "en", "lines": [
        {"scene": "intro", "text": "Hello.", "delivery": "hook"},
    ]})
    wav = tmp_path / "out.wav"
    write_wav(wav)
    [entry] = voice_entries(narration, [wav], lambda _: (0.0, 0.1), tts)
    reference = tts.reference_for(SpeechRequest("Hello.", wav, language="en", delivery="hook"))
    assert entry["reference"] == {
        "file": str(refs["en"]["hook"]), "sha256": reference.sha256,
        "remote_name": "references/en/hook.wav",
    }


def test_config_paths_are_relative_to_project_not_the_working_directory(tmp_path: Path) -> None:
    settings = make_settings(tmp_path)
    refs = settings.chatterbox.references
    for language in ("pt-BR", "en"):
        assert set(refs[language]) == set(TONES)
        for tone, path in refs[language].items():
            assert path == tmp_path / "data" / "voice-references" / language / f"{tone}-01.wav"
            path.parent.mkdir(parents=True, exist_ok=True)
            write_wav(path)
    for provider in ("chatterbox", "chatterbox_modal"):
        tts = LazyContext(settings).tts_named(provider)
        req = SpeechRequest("Hello.", tmp_path / "out.wav", language="en", delivery="hook")
        assert tts.reference_for(req).path == refs["en"]["hook"]


@pytest.mark.parametrize("references", [
    {"xx": {"hook": "voice.wav"}},
    {"en": {"angry": "voice.wav"}},
    {"en": {"hook": "voice.m4a"}},
])
def test_invalid_reference_configuration_is_rejected(references: dict[str, dict[str, str]]) -> None:
    with pytest.raises(ValidationError):
        ChatterboxSettings.model_validate({"references": references})
