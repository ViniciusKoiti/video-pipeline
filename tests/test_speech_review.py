"""Conferência da fala depois da voz (ADR 062): o que o reconhecedor ouviu, comparado com o roteiro e com o
glossário; adaptador do Whisper local com o pipeline falso; folha de escuta."""

from __future__ import annotations

import shutil
import wave
from pathlib import Path
from typing import Any

import pytest

from app.media.listening_sheet import build_sheet, sheet_filter
from app.media.pronunciation import Glossary
from app.pipeline.schemas import Scene, ScenesManifest
from app.pipeline.voice.speech_review import hear_scene, review_speech, sound
from app.providers.alignment.base import TimedWord
from app.providers.alignment.whisper_local import WhisperLocalWordAligner
from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput

GLOSSARY = Glossary.model_validate({"termos": [
    {"escrita": "Thorfinn", "fala": "Tórfin"},
    {"escrita": "Oath", "fala": "ôuf"},
    {"escrita": "An Empty Man", "fala": "én émpti mén"},
]})


def scene(text: str, sid: str = "S01") -> Scene:
    return Scene.model_validate({"id": sid, "narration": text, "visual_need": "contextual_stock",
                                 "search_query": "x"})


def heard(text: str) -> list[TimedWord]:
    return [TimedWord(word, i * 400, i * 400 + 300) for i, word in enumerate(text.split())]


def differences(narration: str, recognized: str) -> list[tuple[str, str, str]]:
    hearing = hear_scene(scene(narration), "voice/S01.wav", heard(recognized), GLOSSARY)
    return [(d.kind, d.expected, d.heard) for d in hearing.differences]


def test_the_same_speech_has_no_difference() -> None:
    text = "Pensa numa anestesia de dentista."
    hearing = hear_scene(scene(text), "v.wav", heard("pensa numa anestesia de dentista"), GLOSSARY)
    assert hearing.differences == [] and hearing.word_error_rate == 0.0


def test_a_swapped_common_word_is_a_difference_with_its_time() -> None:
    """"sem curso de ligação" no lugar de "sem custo de ligação" (S21 do `vazio-de-ter-tudo`)."""
    hearing = hear_scene(scene("O CVV atende sem custo de ligação."), "v.wav",
                         heard("o cvv atende sem curso de ligação"), GLOSSARY)
    (only,) = hearing.differences
    assert (only.kind, only.expected, only.heard) == ("palavra", "custo", "curso")
    assert (only.start_ms, only.end_ms) == (1600, 1900)
    assert hearing.word_error_rate == round(1 / 7, 3)


def test_short_words_and_numbers_written_as_digits_are_recognizer_noise() -> None:
    assert differences("Faz isso três vezes de novo.", "faz isso 3 vezes do novo") == []


def test_a_missing_content_word_is_a_difference() -> None:
    assert differences("Ela faz o dente parar de doer, mas não tira a cárie.",
                       "ela faz o dente parar de doer mas não tira a") == [("palavra", "cárie.", "")]


@pytest.mark.parametrize("recognized", ["Torfin", "Thorfinn", "Tofin", "tórfin"])
def test_a_term_heard_close_to_its_spelling_or_its_glossary_speech_passes(recognized: str) -> None:
    assert differences("Thorfinn é escravo numa fazenda.", f"{recognized} é escravo numa fazenda") == []


def test_a_term_heard_as_something_else_is_a_term_difference() -> None:
    """"Oath" saiu "Wolf"; "An Empty Man" saiu "em Man" (00:05:43 e 00:00:46 do vídeo)."""
    found = differences("No episódio seguinte, chamado Oath, ele jura.",
                        "no episódio seguinte chamado wolf ele jura")
    assert found == [("termo", "Oath,", "wolf")]
    found = differences("O episódio se chama An Empty Man, em português.",
                        "o episódio se chama em man em português")
    assert found == [("termo", "An Empty Man,", "em man")]  # sem uma segunda diferença como "palavra"


def test_the_glossary_speech_comes_with_the_term_difference() -> None:
    hearing = hear_scene(scene("Chamado Oath."), "v.wav", heard("chamado wolf"), GLOSSARY)
    assert hearing.differences[0].spoken_as == "ôuf"


def test_sound_drops_accents_h_and_double_letters() -> None:
    assert sound("Thorfinn") == sound("Tórfin") == "torfin"


class Recognizer:
    def __init__(self, texts: dict[str, str]) -> None:
        self.info = ProviderInfo("fake-ouvido", remote=False)
        self.texts, self.prompts = texts, []

    def recognize_words(self, audio: Path, language: str, prompt: str = "") -> list[TimedWord]:
        self.prompts.append(prompt)
        return heard(self.texts[audio.stem])


def test_review_listens_without_the_expected_text_and_orders_terms_first(tmp_path: Path) -> None:
    raw = {"episode_id": "ep", "language": "pt-BR", "scenes": [
        {"id": sid, "narration": text, "visual_need": "contextual_stock", "search_query": "x"}
        for sid, text in (("S01", "Sem custo de ligação."), ("S02", "Chamado Oath."))
    ]}
    wavs = {"S01": tmp_path / "voice" / "S01.wav", "S02": tmp_path / "voice" / "S02.wav"}
    recognizer = Recognizer({"S01": "sem curso de ligação", "S02": "chamado wolf"})
    review = review_speech(recognizer, ScenesManifest.model_validate(raw), wavs, GLOSSARY, tmp_path)
    assert recognizer.prompts == ["", ""]  # o texto esperado "corrigiria" o nome mal dito
    assert [(d.scene_id, d.kind) for d in review.differences] == [("S02", "termo"), ("S01", "palavra")]
    assert review.scenes[0].wav == "voice/S01.wav" and review.recognizer == "fake-ouvido"


def test_whisper_local_maps_language_converts_chunks_and_loads_once() -> None:
    calls: list[dict[str, Any]] = []
    loads: list[tuple[str, int]] = []

    def recognizer(path: str, **options: Any) -> dict[str, Any]:
        calls.append({"path": path, **options})
        return {"text": " Oi, Tórfin.", "chunks": [
            {"text": " Oi,", "timestamp": (0.0, 0.32)}, {"text": " ", "timestamp": (0.32, 0.33)},
            {"text": " Tórfin.", "timestamp": (0.4, None)},
        ]}

    def load(model: str, threads: int) -> Any:
        loads.append((model, threads))
        return recognizer

    aligner = WhisperLocalWordAligner(model="openai/whisper-small", num_threads=4, load=load)
    words = aligner.recognize_words(Path("S01.wav"), "pt-BR", prompt="Oi, Thorfinn.")
    aligner.recognize_words(Path("S02.wav"), "en")
    assert words == [TimedWord("Oi,", 0, 320), TimedWord("Tórfin.", 400, 400)]
    assert loads == [("openai/whisper-small", 4)] and aligner.info.remote is False
    assert calls[0]["generate_kwargs"] == {"task": "transcribe", "language": "portuguese"}  # sem o prompt
    assert calls[1]["generate_kwargs"]["language"] == "english"
    assert calls[0]["return_timestamps"] == "word"


def test_whisper_local_refuses_a_word_without_time() -> None:
    aligner = WhisperLocalWordAligner(
        model="m", load=lambda *_: lambda *a, **k: {"chunks": [{"text": "oi", "timestamp": (None, None)}]}
    )
    with pytest.raises(InvalidOutput, match="palavra sem tempo"):
        aligner.recognize_words(Path("S01.wav"), "pt-BR")


def test_the_sheet_filter_cuts_each_clip_with_padding_and_silence_between() -> None:
    graph = sheet_filter([(Path("a.wav"), 1000, 1500), (Path("b.wav"), 200, 400)], pad_ms=700, gap_ms=900)
    assert "[0:a]atrim=start=0.300:end=2.200" in graph and "[1:a]atrim=start=0.000:end=1.100" in graph
    assert "anullsrc=r=48000:cl=mono,atrim=duration=0.900[g0]" in graph
    assert graph.endswith("[c0][g0][c1]concat=n=3:v=0:a=1[out]")


def write_wav(path: Path, seconds: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(24000)
        out.writeframes(b"\x10\x00" * int(24000 * seconds))


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="sem ffmpeg")
def test_the_sheet_is_one_mono_wav_with_the_clips_in_order(tmp_path: Path) -> None:
    first, second = tmp_path / "S01.wav", tmp_path / "S02.wav"
    write_wav(first, 3.0)
    write_wav(second, 2.0)
    clips = [(first, 1000, 1500), (second, 0, 300)]
    out = build_sheet(clips, tmp_path / "folha.wav", pad_ms=500, gap_ms=1000)
    with wave.open(str(out)) as sheet:
        seconds = sheet.getnframes() / sheet.getframerate()
        assert sheet.getnchannels() == 1 and sheet.getframerate() == 48000
    assert seconds == pytest.approx(1.5 + 1.0 + 0.8, abs=0.05)
    assert not (tmp_path / "folha.partial.wav").exists()
