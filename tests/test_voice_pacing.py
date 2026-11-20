"""Cadência das pausas (`voice/cadencia.json`): o silêncio de cada fim de frase sai do papel da frase."""

from __future__ import annotations

import math
import struct
import wave
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.media.models.scene_pacing import ScenePacing
from app.media.models.voice_pacing import VoicePacing
from app.media.pacing_plan import gap, load_pacing, pacing_plan, sentences
from app.media.probe import duration_ms
from app.media.voice_pacing import edits, pace_voice, silences
from app.pipeline.governance.state import load_state
from app.pipeline.models.naming import Naming
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.schemas import Status, Step
from app.pipeline.voice.narrator import Narrator, VoiceLibrary
from app.pipeline.voice.state import produce_with_state
from app.storage.json_files import JsonFileStore
from tests.fakes import FakeBatchTTS, wav_duration_ms

P = VoicePacing()
RATE = 24000


def tone_wav(path: Path, pattern: list[tuple[str, float]]) -> Path:
    """WAV mono de 16 bits: trechos de tom ("fala") e de silêncio, em segundos."""
    frames = bytearray()
    for kind, seconds in pattern:
        for n in range(round(seconds * RATE)):
            value = int(12000 * math.sin(2 * math.pi * 220 * n / RATE)) if kind == "fala" else 0
            frames += struct.pack("<h", value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(RATE)
        writer.writeframes(bytes(frames))
    return path


def test_sentences_drop_pause_marks_and_a_period_before_lowercase_does_not_split() -> None:
    text = "A conta começa. <short pause> Quantos vão? E quantos pagam! O dr. silva disse sim."
    expected = ["A conta começa.", "Quantos vão?", "E quantos pagam!", "O dr. silva disse sim."]
    assert sentences(text) == expected
    assert sentences("Uma frase só") == ["Uma frase só"]


@pytest.mark.parametrize(("before", "after", "delivery", "expected"), [
    ("Quantos estão lá ao mesmo tempo?", "A conta começa pelo Caio.", "neutral", P.pergunta_s),
    ("A academia cresceu.", "E a base caiu.", "neutral", P.continuacao_s),
    ("A academia cresceu.", "Só que a base caiu.", "neutral", P.continuacao_s),
    ("A academia cresceu.", "Então, de onde vem o dinheiro?", "neutral", P.conclusao_s),
    ("A academia cresceu.", "A base caiu.", "neutral", P.ponto_s),
    ("A academia cresceu?", "E a base caiu.", "turn", P.virada_s),  # a entrega da próxima manda
    ("Você já pagou sem ir?", None, "neutral", P.final_s),
])
def test_gap_follows_the_role_of_the_sentence(
    before: str, after: str | None, delivery: str, expected: float
) -> None:
    assert gap(before, after, P, after_delivery=delivery) == expected


def test_a_long_sentence_gets_an_extra_breath() -> None:
    long = " ".join(["palavra"] * P.frase_longa_palavras) + "."
    assert gap(long, "A base caiu.", P) == round(P.ponto_s + P.frase_longa_extra_s, 3)


def test_plan_covers_internal_boundaries_and_the_tail_up_to_the_next_scene() -> None:
    lines = [
        ("Como a academia ganha? <short pause> Ninguém sabe.", "hook"),
        ("E a resposta fica para o fim.", "neutral"),
        ("Então, quem paga?", "turn"),
        ("Fim.", "invite"),
    ]
    assert pacing_plan(lines, P) == [
        ScenePacing((P.pergunta_s,), P.continuacao_s),
        ScenePacing((), P.virada_s),  # a cena seguinte tem entrega `turn`
        ScenePacing((), P.virada_s),  # a seguinte é `invite`
        ScenePacing((), P.final_s),
    ]


def test_edits_reshape_head_internal_sentence_silence_and_tail() -> None:
    found = [(0.0, 0.1), (1.5, 2.4), (2.8, 3.0), (4.0, 5.0)]  # a vírgula (0,2 s) fica como está
    cuts, note = edits(found, 5.0, ScenePacing((0.4,), 1.0))
    assert note == "internas=1"
    assert cuts == [
        (0.0, pytest.approx(0.04), 0.0),  # mantém 60 ms antes da fala (≥ 50 ms de cabeça)
        (pytest.approx(1.56), pytest.approx(2.34), pytest.approx(0.28)),
        (pytest.approx(4.06), 5.0, pytest.approx(0.89)),  # 1,0 s menos a cabeça da próxima e a margem
    ]


def test_edits_keep_internal_silences_when_the_count_does_not_match_the_text() -> None:
    cuts, note = edits([(1.0, 1.9), (2.5, 3.4)], 4.0, ScenePacing((0.4,), 0.65))
    assert note == "internas_mantidas(2!=1)"
    assert len(cuts) == 2  # só cabeça e cauda


def test_pace_voice_writes_a_copy_with_the_planned_silences(tmp_path: Path) -> None:
    raw = tone_wav(tmp_path / "voice" / "S01-azure.wav", [
        ("fala", 1.0), ("silêncio", 0.9), ("fala", 1.1), ("silêncio", 0.8),
    ])
    before = raw.read_bytes()
    folder = tmp_path / "voice" / "paced"
    out, note = pace_voice(raw, ScenePacing((0.4,), 1.0), folder)
    assert note == "internas=1" and out.parent == folder and raw.read_bytes() == before
    # 0,05 de cabeça + 1,0 de fala + 0,4 de pausa + 1,1 de fala + 0,95 de cauda (a próxima traz 0,05)
    assert duration_ms(out) == pytest.approx(3500, abs=40)
    found, total = silences(out)
    inner = [(s, e) for s, e in found if 0.5 < s < total - 1.2]
    assert len(inner) == 1 and inner[0][1] - inner[0][0] == pytest.approx(0.4, abs=0.03)
    stamp = out.stat().st_mtime_ns
    assert pace_voice(raw, ScenePacing((0.4,), 1.0), folder)[0] == out and out.stat().st_mtime_ns == stamp
    assert pace_voice(raw, ScenePacing((0.4,), 0.65), folder)[0] != out  # outro plano, outra cópia


def test_pacing_file_is_optional_and_validated(tmp_path: Path) -> None:
    assert load_pacing(tmp_path) is None
    (tmp_path / "voice").mkdir()
    (tmp_path / "voice" / "cadencia.json").write_text('{"pergunta_s": 1.2}')
    assert load_pacing(tmp_path) == VoicePacing(pergunta_s=1.2)
    with pytest.raises(ValidationError):
        VoicePacing(ponto_s=-1)


def test_produce_with_state_hands_the_paced_copy_to_the_assembly(tmp_path: Path) -> None:
    store = JsonFileStore(tmp_path / "data" / "episodes")
    store.path("ep", "").mkdir(parents=True)
    library = VoiceLibrary(store.path("ep", "voice"), Naming.LONG)
    narrator = Narrator(FakeBatchTTS(), "pt-BR", library, lambda wav: wav_duration_ms(wav) / 1000)
    lines = [SpeechLine("S01", "Primeira fala. Segunda frase."), SpeechLine("S02", "Fim.")]
    now = datetime(2026, 11, 15, 12, 0, tzinfo=UTC)
    outcomes = produce_with_state(narrator, store, "ep", lines, now=now, pacing=P)
    assert all(o.status is Status.COMPLETED and o.value and o.value.parent.name == "paced" for o in outcomes)
    record = load_state(store, "ep").get(Step.VOICE).scenes["S01"]
    assert record.outputs[0].startswith("voice/paced/") and "cadencia-v1" in (record.detail or "")
