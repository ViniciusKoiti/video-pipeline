"""`vp voice --conferir` e `--refazer` (ADR 062): ouvir a fala pronta e pedir outra tomada de cenas
escolhidas, sem rede e sem TTS real."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

import pytest

from app.pipeline.voice.retake import RetakeError, set_aside
from tests.fakes import FakeBatchTTS
from tests.test_speech_review import Recognizer
from tests.test_voice_command import run, setup, wavs
from tests.test_voice_scripts import EP

NOW = datetime(2026, 11, 16, 21, 30).astimezone()


def stems(store_wavs: list[str]) -> dict[str, str]:
    return {name.split("-")[0]: Path(name).stem for name in store_wavs}


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="sem ffmpeg")
def test_conferir_alone_listens_writes_the_report_and_the_sheet_and_makes_no_speech(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store, context = setup(tmp_path)
    assert run(context) == 0
    names = stems(wavs(store))
    context.speech_checker = Recognizer({names["S01"]: "primeira cena", names["S02"]: "uma frase com jason"})
    context.tts = FakeBatchTTS()
    capsys.readouterr()
    assert run(context, "--conferir") == 0
    out = capsys.readouterr().out
    assert context.tts.calls == []  # `--conferir` sozinho só ouve
    assert "1 trecho(s) para ouvir" in out and '"JSON."' in out and "-> ouvido \"jason\"" in out
    assert f"vp voice {EP} --voz-final --refazer S02" in out
    report = json.loads(store.path(EP, "voice/conferencia.json").read_text())
    assert report["recognizer"] == "fake-ouvido" and report["scenes"][1]["differences"][0]["heard"] == "jason"
    assert store.path(EP, "voice/conferencia-escuta.wav").is_file()


def test_conferir_without_speech_says_to_run_the_voice_first(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, context = setup(tmp_path)
    context.speech_checker = Recognizer({})
    assert run(context, "--conferir") == 1
    assert "rode o `vp voice` antes de conferir" in capsys.readouterr().err


def test_conferir_with_nothing_different_makes_no_sheet(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store, context = setup(tmp_path)
    assert run(context) == 0
    names = stems(wavs(store))
    context.speech_checker = Recognizer({names["S01"]: "primeira cena", names["S02"]: "uma frase com json"})
    assert run(context, "--conferir") == 0
    assert "nenhuma diferença" in capsys.readouterr().out
    assert not store.path(EP, "voice/conferencia-escuta.wav").exists()


def test_refazer_sets_the_take_aside_and_makes_a_new_one(tmp_path: Path) -> None:
    store, context = setup(tmp_path)
    assert run(context) == 0
    before = wavs(store)
    again = FakeBatchTTS()
    context.tts = again
    assert run(context, "--refazer", "S02") == 0
    assert len(again.calls) == 1 and [name.split("-")[0] for name in again.calls[0]] == ["S02"]
    assert wavs(store) == before  # mesmo texto, mesmo nome: a tomada nova ocupa o lugar
    rejected = list(store.path(EP, "voice/tomadas-recusadas").rglob("*.wav"))
    assert [p.name for p in rejected] == [name for name in before if name.startswith("S02")]


def test_set_aside_moves_raw_and_copies_of_one_voice_only(tmp_path: Path) -> None:
    voice = tmp_path / "voice"
    files = [
        "S06-chatterbox_modal-aaa.wav", "leveled/S06-chatterbox_modal-aaa-111.wav",
        "leveled/S06-chatterbox_modal-aaa-111.json", "paced/S06-chatterbox_modal-aaa-111-222.wav",
        "S06-kokoro-bbb.wav", "S60-chatterbox_modal-ccc.wav",
    ]
    for name in files:
        (voice / name).parent.mkdir(parents=True, exist_ok=True)
        (voice / name).write_bytes(b"x")
    moved = set_aside(voice, ["S06"], ["S06", "S60"], "chatterbox_modal", NOW)
    target = voice / "tomadas-recusadas" / "2026-11-16-213000"
    assert sorted(p.relative_to(target).as_posix() for p in moved) == sorted(files[:4])
    assert (voice / "S06-kokoro-bbb.wav").exists() and (voice / "S60-chatterbox_modal-ccc.wav").exists()


def test_set_aside_refuses_unknown_scenes_and_scenes_without_speech(tmp_path: Path) -> None:
    (tmp_path / "voice").mkdir()
    with pytest.raises(RetakeError, match="fora do roteiro: S99"):
        set_aside(tmp_path / "voice", ["S99"], ["S01"], "kokoro", NOW)
    with pytest.raises(RetakeError, match="sem fala para refazer: S01"):
        set_aside(tmp_path / "voice", ["S01"], ["S01"], "kokoro", NOW)
