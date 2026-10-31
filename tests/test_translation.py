"""Tradução em pasta própria (ADR 034): números ditos, conferência em código e o gate de tradução."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.pipeline.gates import GateError, gate_report, record_decision
from app.pipeline.schemas import Decision, Step
from app.pipeline.translation import (
    Narration,
    content_problems,
    narration_problems,
    spoken_numbers,
    translation_problems,
)
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import FIXED_TIME

SOURCE, TARGET = "lista-pt", "lista-en"


@pytest.mark.parametrize(
    ("text", "language", "expected"),
    [
        ("Com mil nós, não muda nada. Com cem mil, já é dez vezes ou mais.", "pt-BR", [1000, 100000, 10]),
        ("A thousand nodes: no change. A hundred thousand, ten times.", "en", [1000, 100000, 10]),
        ("os mesmos dez milhões de nós", "pt-BR", [10_000_000]),
        ("the same ten million nodes", "en", [10_000_000]),
        ("uns trinta milissegundos, dois segundos. Oitenta a noventa vezes", "pt-BR", [30, 2, 80, 90]),
        ("about thirty milliseconds, over two seconds. Eighty to ninety times", "en", [30, 2, 80, 90]),
        ("vinte e cinco, depois dois mil e quinhentos", "pt-BR", [25, 2500]),
        ("twenty-five, then two thousand five hundred", "en", [25, 2500]),
        ("Uma lista. One list.", "pt-BR", []),  # um/uma e one ficam de fora (limite documentado)
        ("26,9 ms e 10.000 nós", "pt-BR", [26.9, 10000]),
        ("26.9 ms and 10,000 nodes", "en", [26.9, 10000]),
        ("Lista 1: <short pause> 2 listas", "pt-BR", [1, 2]),
        ("1 mil nós, 100 mil nós, 1 milhão de nós", "pt-BR", [1000, 100000, 1000000]),
        ("10 milhões de nós", "pt-BR", [10000000]),
        ("1 thousand, 100 thousand, 1.5 million nodes; 3 2", "en", [1000, 100000, 1500000, 3, 2]),
    ],
)
def test_spoken_numbers(text: str, language: str, expected: list[float | int]) -> None:
    assert spoken_numbers(text, language) == expected


def narration(language: str, *texts: str) -> Narration:
    return Narration.model_validate(
        {"language": language, "lines": [{"scene": f"c{i}", "text": t} for i, t in enumerate(texts, 1)]}
    )


def test_a_clean_translation_has_no_problems() -> None:
    pt = narration("pt-BR", "Dez milhões de nós.", "Só soma.")
    en = narration("en", "Ten million nodes.", "It just adds.")
    assert narration_problems(pt, en) == []


def test_a_changed_number_is_reported_by_scene() -> None:
    pt = narration("pt-BR", "Dez milhões de nós.")
    en = narration("en", "One million nodes... two seconds.")
    [problem] = narration_problems(pt, en)
    assert problem.startswith("c1: números ditos") and "10000000" in problem


def test_scene_delivery_pause_and_language_mismatches() -> None:
    pt = Narration.model_validate(
        {"language": "pt-BR", "lines": [{"scene": "a", "text": "Olha <short pause> aí", "delivery": "hook"}]}
    )
    en = Narration.model_validate(
        {"language": "pt-BR", "lines": [{"scene": "b", "text": "Look at this", "delivery": "turn"}]}
    )
    text = " | ".join(narration_problems(pt, en))
    assert "mesmo do original" in text and "a cena é 'b'" in text
    assert "entrega 'turn'" in text and "pausas" in text


def test_missing_lines_are_reported() -> None:
    pt = narration("pt-BR", "um dois", "três")
    en = narration("en", "one two")
    assert "1 fala(s) na tradução, 2 no original" in narration_problems(pt, en)


def test_content_numbers_and_scene_types_must_match() -> None:
    pt = {"scenes": [{"id": "a", "type": "number", "value": 10}]}
    assert content_problems(pt, {"scenes": [{"id": "a", "type": "number", "value": 10}]}) == []
    assert len(content_problems(pt, {"scenes": [{"id": "a", "type": "number", "value": 11}]})) == 1
    assert "id e tipo" in content_problems(pt, {"scenes": [{"id": "a", "type": "hook", "value": 10}]})[0]


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False))


def pair(tmp_path: Path, en_text: str = "Ten million nodes.") -> tuple[JsonFileStore, JsonReviewGate]:
    store = JsonFileStore(tmp_path / "data" / "episodes")
    write_json(
        store.path(SOURCE, "narracao.json"),
        {"language": "pt-BR", "lines": [{"scene": "a", "text": "Dez milhões de nós."}]},
    )
    write_json(
        store.path(TARGET, "narracao.json"),
        {"language": "en", "lines": [{"scene": "a", "text": en_text}]},
    )
    write_json(
        store.path(TARGET, "traducao.json"),
        {"derived_from": SOURCE, "language": "en", "source_language": "pt-BR"},
    )
    return store, JsonReviewGate(store)


def approve(store: JsonFileStore, review: JsonReviewGate):
    return record_decision(
        store, review, TARGET, Step.TRANSLATION, Decision.APPROVED, reviewer="Dono", now=lambda: FIXED_TIME
    )


def test_translation_problems_reads_the_original_from_the_link(tmp_path: Path) -> None:
    store, _ = pair(tmp_path)
    assert translation_problems(store, TARGET) == []
    store, _ = pair(tmp_path / "outra", en_text="One million nodes.")
    assert len(translation_problems(store, TARGET)) == 1


def test_missing_link_or_original_is_a_problem(tmp_path: Path) -> None:
    store = JsonFileStore(tmp_path / "data" / "episodes")
    assert "falta arquivo" in translation_problems(store, TARGET)[0]


def test_approval_is_blocked_while_the_check_finds_problems(tmp_path: Path) -> None:
    store, review = pair(tmp_path, en_text="One million nodes.")
    with pytest.raises(GateError, match="vp traducao"):
        approve(store, review)
    assert review.log(TARGET).entries == []


def test_approval_is_stamped_and_falls_when_the_original_changes(tmp_path: Path) -> None:
    store, review = pair(tmp_path)
    approve(store, review)
    [row] = [r for r in gate_report(store, review, TARGET) if r.step is Step.TRANSLATION]
    assert row.valid
    write_json(
        store.path(SOURCE, "narracao.json"),
        {"language": "pt-BR", "lines": [{"scene": "a", "text": "Dez milhões de nós, de novo."}]},
    )
    [row] = [r for r in gate_report(store, review, TARGET) if r.step is Step.TRANSLATION]
    assert not row.valid


def test_only_translation_folders_list_the_translation_gate(tmp_path: Path) -> None:
    store, review = pair(tmp_path)
    assert Step.TRANSLATION not in [r.step for r in gate_report(store, review, SOURCE)]
    assert Step.TRANSLATION in [r.step for r in gate_report(store, review, TARGET)]


def test_folder_without_link_has_no_translation_gate(tmp_path: Path) -> None:
    store, review = pair(tmp_path)
    with pytest.raises(GateError, match="não é uma tradução"):
        record_decision(
            store, review, SOURCE, Step.TRANSLATION, Decision.APPROVED,
            reviewer="Dono", now=lambda: FIXED_TIME,
        )
