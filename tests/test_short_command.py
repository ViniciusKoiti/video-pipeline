"""RF7: `vp short voz` e `vp short gate`; os limites da fala; sem rede e sem TTS real."""

from __future__ import annotations

import json
import math
import os
import struct
import wave
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.media.speech_bounds import SpeechBoundsError, bounds_from_log, speech_bounds
from app.storage.json_files import JsonFileStore
from tests.fakes import FakeBatchTTS, wav_duration_ms

EP = "short-voz"
LINES = [
    {"scene": "gancho", "text": " Uma lista ligada. ", "delivery": "hook"},
    {"scene": None, "text": "Fala solta, sem cena."},
    {"scene": "final", "text": "Até a próxima.", "delivery": "invite"},
]


def write_tone(path: Path, pattern: list[tuple[str, float]]) -> None:
    """WAV de 16 kHz: `("silence"|"tone", segundos)` em sequência."""
    rate, frames = 16000, bytearray()
    for kind, seconds in pattern:
        for i in range(int(rate * seconds)):
            sample = 0 if kind == "silence" else int(12000 * math.sin(2 * math.pi * 440 * i / rate))
            frames += struct.pack("<h", sample)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(bytes(frames))


# --- limites da fala ---------------------------------------------------------------------------------------


def test_the_speech_sits_between_the_edge_silences() -> None:
    log = "silence_start: 0\nsilence_end: 0.45\nsilence_start: 3.5\nsilence_end: 3.92\n"
    begin, end = bounds_from_log(log, 3.92)
    assert begin == pytest.approx(0.37) and end == pytest.approx(3.58)
    # um silêncio do meio não mexe nas pontas; sem silêncio nas pontas, o arquivo inteiro
    assert bounds_from_log("silence_start: 1.1\nsilence_end: 1.4\n", 3.2) == (0.0, 3.2)
    assert bounds_from_log("silence_start: 2.65\n", 3.2) == (0.0, pytest.approx(2.73))  # aberto até o fim
    assert bounds_from_log("silence_start: 0\nsilence_end: 3.2\n", 3.2) == (0.0, 3.2)  # só silêncio


def test_the_bounds_of_a_real_wav_come_from_ffmpeg(tmp_path: Path) -> None:
    wav = tmp_path / "a.wav"
    write_tone(wav, [("silence", 0.6), ("tone", 0.8), ("silence", 0.5)])
    begin, end = speech_bounds(wav)
    assert begin == pytest.approx(0.52, abs=0.05) and end == pytest.approx(1.48, abs=0.05)


def test_a_file_ffmpeg_cannot_read_is_a_project_error(tmp_path: Path) -> None:
    broken = tmp_path / "ruim.wav"
    broken.write_bytes(b"isto nao e audio")
    with pytest.raises(SpeechBoundsError, match="ruim.wav"):
        speech_bounds(broken)


# --- vp short voz ------------------------------------------------------------------------------------------


def make(tmp_path: Path, **voices: FakeBatchTTS) -> tuple[Path, Path, SimpleNamespace]:
    folder = tmp_path / "episodes" / EP
    folder.mkdir(parents=True)
    narration = folder / "narracao.pt.json"
    narration.write_text(json.dumps({"language": "pt-BR", "lines": LINES}), encoding="utf-8")
    providers = SimpleNamespace(tts="kokoro", tts_final=voices.pop("final_name", None))
    named = {"kokoro": voices.get("kokoro", FakeBatchTTS())}
    context = SimpleNamespace(
        store=JsonFileStore(tmp_path / "episodes"),
        settings=SimpleNamespace(providers=providers),
        tts=FakeBatchTTS(),
        tts_final=voices.get("final", FakeBatchTTS()),
        tts_named=named.__getitem__,
    )
    return folder, narration, context


def voz(context: SimpleNamespace, folder: Path, narration: Path, *extra: str) -> int:
    args = build_parser().parse_args(["short", "voz", str(folder), str(narration), *extra])
    return handled("vp short", lambda: HANDLERS["short"](args, context))  # type: ignore[arg-type]


def test_the_final_voice_makes_one_wav_per_line_and_writes_the_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("HF_HUB_OFFLINE", "x")
    monkeypatch.delenv("HF_HUB_OFFLINE")  # o valor de fora não conta: o comando é que o define
    folder, narration, context = make(tmp_path, final_name="chatterbox_modal")
    assert voz(context, folder, narration) == 0
    assert os.environ["HF_HUB_OFFLINE"] == "1"
    assert len(context.tts_final.calls) == 1 and context.tts.calls == []
    record = json.loads((folder / "narracao.pt.voz.json").read_text(encoding="utf-8"))
    assert record["language"] == "pt-BR" and record["provider"] == "chatterbox_modal"
    scenes = [(item["scene"], item["text"], item["delivery"]) for item in record["lines"]]
    assert scenes == [
        ("gancho", "Uma lista ligada.", "hook"),
        (None, "Fala solta, sem cena.", "neutral"),
        ("final", "Até a próxima.", "invite"),
    ]
    for item in record["lines"]:
        wav = folder / item["wav"]
        begin, end = item["speech"]
        assert item["seconds"] == wav_duration_ms(wav) / 1000 and 0 <= begin < end <= item["seconds"] + 0.01
    assert [item["wav"].split("-fake-ptbr-")[0] for item in record["lines"]] == [
        "voice/gancho", "voice/fora-1", "voice/final",
    ]
    out = capsys.readouterr().out.splitlines()
    assert [line.split()[0] for line in out[:3]] == ["gancho", "fora", "final"]
    assert out[-1].startswith("voz: 3 fala(s), ") and out[-1].endswith("registro em narracao.pt.voz.json")


def test_a_named_voice_replaces_the_final_one_and_nothing_is_generated_twice(tmp_path: Path) -> None:
    kokoro = FakeBatchTTS()
    folder, narration, context = make(tmp_path, kokoro=kokoro, final_name="chatterbox_modal")
    assert voz(context, folder, narration, "--voz", "kokoro") == 0
    assert len(kokoro.calls) == 1 and context.tts_final.calls == []
    assert json.loads((folder / "narracao.pt.voz.json").read_text())["provider"] == "kokoro"
    assert voz(context, folder, narration, "--voz", "kokoro") == 0
    assert len(kokoro.calls) == 1  # as falas prontas não voltam à voz


def test_without_a_final_voice_in_the_config_the_record_names_the_draft_voice(tmp_path: Path) -> None:
    folder, narration, context = make(tmp_path)
    assert voz(context, folder, narration) == 0
    assert json.loads((folder / "narracao.pt.voz.json").read_text())["provider"] == "kokoro"
    assert len(context.tts_final.calls) == 1  # o motor é o `tts_final` do contexto


def test_a_broken_narration_stops_before_any_voice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = make(tmp_path)
    narration.write_text(json.dumps({"language": "pt-BR", "lines": []}), encoding="utf-8")
    assert voz(context, folder, narration) == 1
    assert "vp short: narracao.pt.json: lines" in capsys.readouterr().err
    assert context.tts_final.calls == [] and not (folder / "narracao.pt.voz.json").exists()


def test_the_state_of_the_voice_run_goes_to_the_folder_manifest(tmp_path: Path) -> None:
    from app.pipeline.schemas import Status, Step
    from app.pipeline.state import load_state

    folder, narration, context = make(tmp_path)
    assert voz(context, folder, narration) == 0
    state = load_state(JsonFileStore(folder.parent), EP).get(Step.VOICE)
    assert state.status is Status.COMPLETED


class RecordingTTS(FakeBatchTTS):
    """Guarda o texto e a entrega que a voz recebeu, na ordem."""

    def __init__(self) -> None:
        super().__init__()
        self.heard: list[tuple[str, str | None]] = []

    def synthesize_many(self, requests):  # type: ignore[no-untyped-def]
        self.heard += [(r.text, r.delivery) for r in requests]
        return super().synthesize_many(requests)


def test_each_line_is_spoken_with_its_delivery_and_the_glossary_spelling(tmp_path: Path) -> None:
    folder, narration, context = make(tmp_path)
    context.tts_final = RecordingTTS()
    (folder / "voice").mkdir()
    glossary = {"termos": [{"escrita": "JSON", "fala": "jêison"}]}
    (folder / "voice" / "glossary.json").write_text(json.dumps(glossary), encoding="utf-8")
    lines = [{"scene": "a", "text": "Um JSON.", "delivery": "turn"}, {"scene": "b", "text": "Outro."}]
    narration.write_text(json.dumps({"language": "pt-BR", "lines": lines}), encoding="utf-8")
    assert voz(context, folder, narration) == 0
    assert context.tts_final.heard == [("Um jêison.", "turn"), ("Outro.", "neutral")]
    record = (folder / "narracao.pt.voz.json").read_text(encoding="utf-8")
    assert '"Um JSON."' in record  # a tela e o registro ficam com a grafia da narração


def test_the_record_keeps_accents_readable_and_the_bounds_rounded_to_milliseconds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = make(tmp_path)
    monkeypatch.setattr("app.commands.short_voz.speech_bounds", lambda wav: (0.12345, 0.98765))
    assert voz(context, folder, narration) == 0
    raw = (folder / "narracao.pt.voz.json").read_text(encoding="utf-8")
    assert "Até a próxima." in raw and raw.endswith("}\n")
    record = json.loads(raw)
    assert [item["speech"] for item in record["lines"]] == [[0.123, 0.988]] * 3
    out = capsys.readouterr().out.splitlines()
    assert "fala 0.12–0.99" in out[0] and ", 2.6 s de fala," in out[-1]  # 3 × (0,988 − 0,123)


def test_a_folder_outside_the_episodes_folder_is_refused_before_any_voice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = make(tmp_path)
    elsewhere = tmp_path / "fora" / EP
    elsewhere.mkdir(parents=True)
    assert voz(context, elsewhere, narration) == 1
    assert "vp short:" in capsys.readouterr().err
    assert context.tts_final.calls == [] and not (elsewhere / "narracao.pt.voz.json").exists()
    assert not (folder / "narracao.pt.voz.json").exists()
