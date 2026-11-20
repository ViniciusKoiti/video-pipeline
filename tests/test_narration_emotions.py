"""Marcas de emoção na narração (ADR 063): somem do texto falado, das legendas e das âncoras; erros e
atenção."""

from __future__ import annotations

from app.media.narration import (
    emotion_segments,
    narration_problems,
    pause_positions,
    split_pauses,
    strip_emotions,
    strip_pauses,
    timeline_length,
)
from app.pipeline.schemas import ScenesManifest
from app.pipeline.script.checks.emotion_marks import emotion_attention

TEXT = "Light é Kira. <raiva>Com raiva, escreve o nome dessa pessoa.</raiva>"


def test_marks_take_no_space_in_the_spoken_text() -> None:
    assert strip_emotions(TEXT) == "Light é Kira. Com raiva, escreve o nome dessa pessoa."
    assert strip_pauses(TEXT) == strip_emotions(TEXT)
    assert split_pauses("<sussurro>E Kira <short pause> mora lá.</sussurro>") == ["E Kira", "mora lá."]
    assert timeline_length(TEXT) == len(strip_emotions(TEXT))


def test_pause_positions_ignore_the_marks() -> None:
    text = "<raiva>Com raiva, <short pause> escreve.</raiva>"
    assert pause_positions(text) == pause_positions(strip_emotions(text))


def test_segments_carry_the_emotion_of_each_passage() -> None:
    expected = [(None, "Light é Kira."), ("raiva", "Com raiva, escreve o nome dessa pessoa.")]
    assert emotion_segments(TEXT) == expected
    assert emotion_segments("Sem marca nenhuma.") == [(None, "Sem marca nenhuma.")]


def test_well_formed_marks_are_not_errors() -> None:
    assert narration_problems(TEXT) == []
    assert narration_problems("<sussurro>E Kira <short pause> mora lá.</sussurro>") == []


def test_unknown_unclosed_nested_and_empty_marks_are_errors() -> None:
    assert any("tag desconhecida" in p for p in narration_problems("<grito>Socorro aqui.</grito>"))
    assert any("sem </raiva>" in p for p in narration_problems("<raiva>Com raiva, escreve."))
    assert any("sem <raiva> aberta" in p for p in narration_problems("Com raiva, escreve.</raiva>"))
    nested = narration_problems("<raiva>Com <sussurro>raiva</sussurro> escreve.</raiva>")
    assert any("dentro de <raiva>" in p for p in nested)
    assert any("vazia" in p for p in narration_problems("Antes <raiva></raiva> depois."))


def _scenes(*narrations: str) -> ScenesManifest:
    scenes = [
        {"id": f"S{i + 1:02d}", "narration": n, "shots": [], "visual_need": "contextual_stock",
         "search_query": "x"}
        for i, n in enumerate(narrations)
    ]
    return ScenesManifest.model_validate({"episode_id": "teste", "language": "pt-BR", "scenes": scenes})


def test_attention_for_short_marks_and_too_many_in_a_scene() -> None:
    short = emotion_attention(_scenes("Ele disse <surpresa>não!</surpresa> e saiu."))
    assert len(short) == 1 and "S01: <surpresa> com 1 palavra" in short[0]
    many = (
        "<raiva>Uma frase longa aqui.</raiva> <tristeza>Outra frase longa aqui.</tristeza> "
        "<firme>Mais uma frase longa.</firme>"
    )
    assert any("3 marcas na cena" in line for line in emotion_attention(_scenes(many)))
    assert emotion_attention(_scenes(TEXT)) == []
