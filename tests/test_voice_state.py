"""RF6 (estado): o relatório por cena da voz fica no manifest.json e o `vp status` o mostra."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.cli import main
from app.pipeline.models.naming import Naming
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.ports import EpisodeLocked
from app.pipeline.schemas import Status, Step
from app.pipeline.state import load_state
from app.pipeline.voice import Narrator, VoiceLibrary
from app.pipeline.voice_state import produce_with_state, voice_pending
from app.providers.errors import QuotaExhausted
from app.storage.json_files import JsonFileStore
from tests.fakes import FakeBatchTTS, make_root, wav_duration_ms

EP = "ep-estado"
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
LINES = [
    SpeechLine("S01", "Primeira fala."),
    SpeechLine("S02", "Segunda fala."),
    SpeechLine("S03", "Terceira."),
]


def narrator(tts: FakeBatchTTS, store: JsonFileStore) -> Narrator:
    library = VoiceLibrary(store.path(EP, "voice"), Naming.LONG)
    return Narrator(tts, "pt-BR", library, lambda wav: wav_duration_ms(wav) / 1000)


def produce(tts: FakeBatchTTS, store: JsonFileStore, lines: list[SpeechLine] = LINES):  # type: ignore[no-untyped-def]
    return produce_with_state(narrator(tts, store), store, EP, lines, now=NOW)


def step(store: JsonFileStore):  # type: ignore[no-untyped-def]
    return load_state(store, EP).get(Step.VOICE)


@pytest.fixture
def store(tmp_path: Path) -> JsonFileStore:
    store = JsonFileStore(tmp_path / "data" / "episodes")
    store.path(EP, "").mkdir(parents=True)
    return store


def test_a_complete_run_records_every_scene_with_its_wav(store: JsonFileStore) -> None:
    outcomes = produce(FakeBatchTTS(), store)
    state = step(store)
    assert state.status is Status.COMPLETED and state.pending_scenes == [] and state.finished_at == NOW
    assert sorted(state.scenes) == ["S01", "S02", "S03"]
    assert state.outputs == [o.value.relative_to(store.path(EP, "")).as_posix() for o in outcomes]
    assert all(r.status is Status.COMPLETED for r in state.scenes.values()) and voice_pending(store, EP) == []


def test_a_partial_run_records_what_is_pending_and_why_and_a_new_process_reads_it(
    store: JsonFileStore, tmp_path: Path
) -> None:
    probe = narrator(FakeBatchTTS(), store)
    bad = probe.key(LINES[1]).file_name(Naming.LONG)
    failing = FakeBatchTTS(max_batch_chars=1, scene_errors={bad: QuotaExhausted("fake", "10 por dia")})
    produce(failing, store)
    state = step(store)
    assert state.status is Status.NEEDS_REVIEW and sorted(state.pending_scenes) == ["S02", "S03"]
    assert state.scenes["S02"].reason == "quota_exhausted" and "10 por dia" in state.scenes["S02"].detail
    assert state.scenes["S01"].status is Status.COMPLETED and len(state.outputs) == 1
    reborn = JsonFileStore(tmp_path / "data" / "episodes")  # outro processo: nada em memória
    assert voice_pending(reborn, EP) == ["voz S02 (quota_exhausted)", "voz S03 (quota_exhausted)"]


def test_resuming_asks_only_for_what_is_missing_and_clears_the_pending_state(store: JsonFileStore) -> None:
    probe = narrator(FakeBatchTTS(), store)
    bad = probe.key(LINES[1]).file_name(Naming.LONG)
    produce(FakeBatchTTS(max_batch_chars=1, scene_errors={bad: QuotaExhausted("fake", "cota")}), store)
    retry = FakeBatchTTS(max_batch_chars=1)
    produce(retry, store)
    assert sorted(n for call in retry.calls for n in call) == sorted(
        [probe.key(LINES[1]).file_name(Naming.LONG), probe.key(LINES[2]).file_name(Naming.LONG)]
    )
    assert step(store).status is Status.COMPLETED and voice_pending(store, EP) == []


def test_a_registered_wav_that_vanished_is_reported_and_a_changed_text_changes_the_input(
    store: JsonFileStore,
) -> None:
    outcomes = produce(FakeBatchTTS(), store)
    before = step(store).input_hash
    outcomes[0].value.unlink()
    assert voice_pending(store, EP) == ["voz S01 (WAV ausente)"]
    produce(FakeBatchTTS(), store)  # rodar de novo refaz só essa
    assert voice_pending(store, EP) == [] and step(store).input_hash == before
    produce(FakeBatchTTS(), store, [SpeechLine("S01", "Texto novo.")])
    assert step(store).input_hash != before


def test_an_unexpected_error_is_recorded_as_failed_and_raised_keeping_what_was_ready(
    store: JsonFileStore,
) -> None:
    produce(FakeBatchTTS(), store)
    ready = dict(step(store).scenes)
    changed = [SpeechLine("S01", "Primeira fala."), SpeechLine("S02", "Outra segunda.")]
    bad = narrator(FakeBatchTTS(), store).key(changed[1]).file_name(Naming.LONG)
    with pytest.raises(KeyError):
        produce(FakeBatchTTS(scene_errors={bad: KeyError("bug")}), store, changed)
    state = step(store)
    assert state.status is Status.FAILED and state.error.startswith("erro_inesperado") and state.scenes == {}
    assert voice_pending(store, EP)[-1].startswith("voz (rodada falhou: erro_inesperado")
    assert ready  # o que estava pronto antes segue nos arquivos
    produce(FakeBatchTTS(), store, changed)
    assert step(store).status is Status.COMPLETED


def test_the_episode_lock_is_held_during_the_run_and_released_after_an_error(store: JsonFileStore) -> None:
    class Locking(FakeBatchTTS):
        def synthesize_many(self, requests):  # type: ignore[no-untyped-def]
            with store.lock(EP):  # aninhar o lock é erro: a geração já o segura
                return super().synthesize_many(requests)

    with pytest.raises(EpisodeLocked):
        produce(Locking(), store)
    assert step(store).status is Status.FAILED
    produce(FakeBatchTTS(), store)  # o lock saiu com a exceção
    assert step(store).status is Status.COMPLETED


def test_vp_status_lists_the_pending_voice_scenes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_root(tmp_path)
    cli_store = JsonFileStore(root / "data" / "episodes")
    folder = cli_store.path(EP, "")
    folder.mkdir(parents=True)
    for name in ("sources.json", "facts.json", "scenes.json", "outline.md"):
        (folder / name).write_text("{}")
    probe = narrator(FakeBatchTTS(), cli_store)
    bad = probe.key(LINES[1]).file_name(Naming.LONG)
    produce(FakeBatchTTS(max_batch_chars=1, scene_errors={bad: QuotaExhausted("fake", "cota")}), cli_store)
    monkeypatch.chdir(root)
    assert main(["status", EP]) == 0
    out = capsys.readouterr().out.strip().splitlines()[-1]
    assert "voz S02 (quota_exhausted)" in out and "voz S03 (quota_exhausted)" in out
    produce(FakeBatchTTS(), cli_store)
    assert main(["status", EP]) == 0
    assert "voz S0" not in capsys.readouterr().out
