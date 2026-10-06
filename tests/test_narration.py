"""Pausas dentro da narração (ADR 015): marcas, validação, tempo dos planos, Kokoro e lotes. Sem rede."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.media.narration import (
    PAUSE_CHARS,
    has_pauses,
    narration_problems,
    pause_positions,
    split_pauses,
    strip_pauses,
    timeline_length,
    timeline_position,
)
from app.pipeline.schemas import Scene
from app.pipeline.shots import shot_bounds
from app.providers.tts.base import SpeechRequest
from app.providers.tts.kokoro import KokoroTTS

SP = "<short pause>"
TEXT = f"Se você quer realmente {SP} aprender sobre isso, você {SP} deve começar pelo dinheiro."
PLAIN = "Se você quer realmente aprender sobre isso, você deve começar pelo dinheiro."


def test_marks_leave_the_plain_text_and_count_in_the_timeline() -> None:
    assert strip_pauses(TEXT) == PLAIN and strip_pauses(PLAIN) == PLAIN
    assert has_pauses(TEXT) and not has_pauses(PLAIN)
    assert split_pauses(TEXT) == [
        "Se você quer realmente", "aprender sobre isso, você", "deve começar pelo dinheiro."
    ]
    assert [PLAIN[p:].split()[0] for p in pause_positions(TEXT)] == ["aprender", "deve"]
    assert timeline_length(TEXT) == len(PLAIN) + 2 * PAUSE_CHARS
    assert timeline_length(PLAIN) == len(PLAIN)
    # um ponto depois de uma pausa anda a pausa inteira; antes dela, nada
    deve = PLAIN.index("deve")
    assert timeline_position(TEXT, PLAIN.index("quer")) == PLAIN.index("quer")
    assert timeline_position(TEXT, PLAIN.index("aprender")) == PLAIN.index("aprender") + PAUSE_CHARS
    assert timeline_position(TEXT, deve) == deve + 2 * PAUSE_CHARS


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (TEXT, []),
        (PLAIN, []),
        ("a <long pause> b", "só do lote de cenas"),
        ("a <breath> b", "tag desconhecida"),
        (f"{SP} a b", "no começo ou no fim"),
        (f"a b {SP}", "no começo ou no fim"),
        (f"a{SP}b", "uma palavra e um espaço de cada lado"),
        (f"a {SP} {SP} b", "uma palavra e um espaço de cada lado"),
        (f"a, {SP}b", "uma palavra e um espaço de cada lado"),
    ],
)
def test_narration_problems(text: str, expected: str | list[str]) -> None:
    problems = narration_problems(text)
    if expected == []:
        assert problems == []
    else:
        assert len(problems) == 1 and expected in problems[0]


def scene(narration: str, shots: list[dict[str, Any]]) -> Scene:
    return Scene.model_validate({"id": "S01", "narration": narration, "shots": shots})


def stamp(anchor: str) -> dict[str, Any]:
    claim = {"text": "t", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E1"]}
    return {"kind": "stamp", "anchor": anchor, "date": "1918", "claims": [claim]}


def test_scene_anchors_live_in_the_text_without_marks() -> None:
    # a âncora atravessa a pausa: "realmente aprender" só existe sem a marca
    ok = scene(TEXT, [stamp("Se você"), stamp("realmente aprender")])
    assert [s.anchor for s in ok.shots] == ["Se você", "realmente aprender"]
    with pytest.raises(ValidationError, match="não aparece na narração"):
        scene(TEXT, [stamp("Se você"), stamp(f"realmente {SP} aprender")])
    with pytest.raises(ValidationError, match="S01: .*tag desconhecida"):
        scene("a <breath> b", [stamp("a")])


def test_marks_shift_the_shots_after_the_pause() -> None:
    shots = scene(TEXT, [stamp("Se você"), stamp("deve começar")]).shots
    plain_shots = scene(PLAIN, [stamp("Se você"), stamp("deve começar")]).shots
    (_, _), (with_pause, _) = shot_bounds(TEXT, shots, 10_000)
    (_, _), (without_pause, _) = shot_bounds(PLAIN, plain_shots, 10_000)
    deve = PLAIN.index("deve")
    assert without_pause == round(deve / len(PLAIN) * 10_000)
    assert with_pause == round((deve + 2 * PAUSE_CHARS) / (len(PLAIN) + 2 * PAUSE_CHARS) * 10_000)
    assert with_pause > without_pause  # duas pausas empurram o plano para depois, onde a fala de fato está


class FakePipeline:
    """Faz de conta do KPipeline: devolve um áudio de 0,5 s de 1.0 por pedaço de texto."""

    def __init__(self) -> None:
        self.texts: list[str] = []

    def __call__(self, text: str, voice: str) -> list[tuple[str, str, Any]]:
        import numpy as np

        self.texts.append(text)
        return [("g", "p", np.ones(12_000, dtype=np.float32))]


def test_kokoro_synthesizes_each_piece_with_silence_between(tmp_path: Path) -> None:
    pytest.importorskip("soundfile")
    np = pytest.importorskip("numpy")
    import soundfile as sf

    tts = KokoroTTS({"pt-BR": "pm_alex"}, pause_ms=500)
    fake = FakePipeline()
    tts._pipelines["p"] = fake
    out = tmp_path / "x.wav"
    tts.synthesize_speech(SpeechRequest(text=TEXT, out_path=out, language="pt-BR"))
    assert fake.texts == split_pauses(TEXT)  # um pedaço por trecho, sem a marca
    audio, rate = sf.read(out)
    assert rate == 24_000
    assert len(audio) == 3 * 12_000 + 2 * 12_000  # 3 trechos de 0,5 s e 2 silêncios de 0,5 s
    assert float(np.abs(audio[12_000:24_000]).max()) == 0.0  # o primeiro silêncio é mudo
    # sem marca, é uma síntese só, como antes
    fake.texts.clear()
    tts.synthesize_speech(SpeechRequest(text=PLAIN, out_path=out, language="pt-BR"))
    assert fake.texts == [PLAIN]


def montar_module() -> Any:
    path = Path(__file__).resolve().parents[1] / "scripts" / "provisorio" / "montar_episodio.py"
    spec = importlib.util.spec_from_file_location("montar_episodio", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_scenes_with_pauses_never_share_a_gemini_batch(tmp_path: Path) -> None:
    montar = montar_module()
    req = lambda text: SpeechRequest(text=text, out_path=tmp_path / "x.wav", language="pt-BR")  # noqa: E731
    plain = [req("Primeira."), req("Segunda."), req("Terceira.")]
    assert [len(g) for g in montar.batches(plain)] == [3]  # sem pausas, juntas, como antes
    mixed = [req("Primeira."), req(f"Com {SP} pausa."), req("Terceira."), req("Quarta.")]
    assert [[r.text for r in g] for g in montar.batches(mixed)] == [
        ["Primeira."], [f"Com {SP} pausa."], ["Terceira.", "Quarta."]
    ]
