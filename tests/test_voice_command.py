"""RF7: `vp voice` gera a narração por cena com a voz escolhida; sem rede e sem TTS real."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.pipeline.models.naming import Naming
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.schemas import Status, Step
from app.pipeline.state import load_state
from app.pipeline.voice import Narrator, VoiceLibrary
from app.providers.errors import QuotaExhausted
from app.providers.tts.base import SpeechRequest
from app.storage.json_files import JsonFileStore
from tests.fakes import FakeBatchTTS, wav_duration_ms
from tests.test_voice_scripts import EP, scenes


class DeliveryTTS(FakeBatchTTS):
    """Como as vozes clonadas: a entrega entra na impressão digital, logo no nome do WAV."""

    def fingerprint(self, request: SpeechRequest) -> str:
        return f"{super().fingerprint(request)}|{request.delivery}"


def setup(tmp_path: Path, **voices: FakeBatchTTS) -> tuple[JsonFileStore, SimpleNamespace]:
    store = JsonFileStore(tmp_path / "episodes")
    store.write(EP, "scenes.json", scenes())
    default, final = voices.get("tts", FakeBatchTTS()), voices.get("final", FakeBatchTTS())
    named = {"gemini": voices.get("gemini", FakeBatchTTS())}
    context = SimpleNamespace(store=store, tts=default, tts_final=final, tts_named=named.__getitem__)
    return store, context


def run(context: SimpleNamespace, *argv: str) -> int:
    args = build_parser().parse_args(["voice", EP, *argv])
    return handled("vp voice", lambda: HANDLERS["voice"](args, context))  # type: ignore[arg-type]


def wavs(store: JsonFileStore) -> list[str]:
    return sorted(p.name for p in store.path(EP, "voice").glob("*.wav"))


def test_the_default_voice_makes_one_wav_per_scene_and_says_the_duration_of_each(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("HF_HUB_OFFLINE", "x")
    monkeypatch.delenv("HF_HUB_OFFLINE")  # o valor de fora não conta: o comando é que o define
    store, context = setup(tmp_path)
    assert run(context) == 0
    out = capsys.readouterr().out.splitlines()
    assert [line.split(":")[0] for line in out[:2]] == ["S01", "S02"]
    total = sum(wav_duration_ms(store.path(EP, "voice") / name) for name in wavs(store))
    assert out[-1].endswith(f"total {total / 1000:.1f} s") and out[-1].startswith("voz: ")
    assert len(wavs(store)) == 2 and len(context.tts.calls) == 1
    assert context.tts_final.calls == [] and os.environ["HF_HUB_OFFLINE"] == "1"
    assert load_state(store, EP).get(Step.VOICE).status is Status.COMPLETED  # o relatório por cena (ADR 052)


def test_each_scene_is_spoken_with_its_own_delivery(tmp_path: Path) -> None:
    store, context = setup(tmp_path, tts=DeliveryTTS())
    assert run(context) == 0
    probe = Narrator(DeliveryTTS(), "pt-BR", VoiceLibrary(tmp_path / "x", Naming.LONG), lambda w: 1.0)
    expected = [
        probe.key(SpeechLine("S01", "Primeira cena.", "neutral")).file_name(Naming.LONG),
        probe.key(SpeechLine("S02", "Uma frase com JSON.", "turn")).file_name(Naming.LONG),
    ]
    assert wavs(store) == sorted(expected)


def test_voz_final_uses_the_final_voice_and_voz_nome_wins_over_it(tmp_path: Path) -> None:
    final, gemini = FakeBatchTTS(), FakeBatchTTS()
    _, context = setup(tmp_path, final=final, gemini=gemini)
    assert run(context, "--voz-final") == 0
    assert (len(final.calls), len(context.tts.calls), len(gemini.calls)) == (1, 0, 0)
    _, other = setup(tmp_path / "b", final=final, gemini=gemini)
    assert run(other, "--voz-final", "--voz", "gemini") == 0
    assert len(gemini.calls) == 1 and len(final.calls) == 1  # a final não rodou de novo


def test_a_repeat_asks_the_voice_for_nothing(tmp_path: Path) -> None:
    store, context = setup(tmp_path)
    assert run(context) == 0
    again = FakeBatchTTS()
    context.tts = again
    assert run(context) == 0
    assert again.calls == [] and len(wavs(store)) == 2


def test_a_quota_stop_keeps_what_is_ready_says_what_is_missing_and_the_next_run_continues(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    probe = Narrator(FakeBatchTTS(), "pt-BR", VoiceLibrary(tmp_path / "x", Naming.LONG), lambda w: 1.0)
    bad = probe.key(SpeechLine("S02", "Uma frase com JSON.", "turn")).file_name(Naming.LONG)
    failing = FakeBatchTTS(max_batch_chars=1, scene_errors={bad: QuotaExhausted("fake", "10 por dia")})
    store, context = setup(tmp_path, tts=failing)
    assert run(context) == 1
    assert "vp voice: 1 fala(s) sem WAV (S02: quota_exhausted" in capsys.readouterr().err
    assert len(wavs(store)) == 1
    context.tts = FakeBatchTTS(max_batch_chars=1)
    assert run(context) == 0 and len(wavs(store)) == 2
    assert [c for call in context.tts.calls for c in call] == [bad]  # só a que faltava


def test_a_missing_scenes_file_is_an_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    context = SimpleNamespace(store=JsonFileStore(tmp_path / "episodes"), tts=FakeBatchTTS())
    assert run(context) == 1
    assert capsys.readouterr().err.startswith("vp voice:")
