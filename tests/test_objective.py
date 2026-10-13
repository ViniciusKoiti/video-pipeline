"""Objetivo do vídeo (ADR 019): noticiar, explicar e opinar, de um a três por roteiro."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from app.pipeline.check import NEWS_MAX_AGE_DAYS, objective_summary, objective_warnings
from app.pipeline.schemas import Objective, ScenesManifest

PROMISE = "A pessoa entende o que o contrato compra."
EXPLAIN = {"kinds": ["explicar"], "promise": PROMISE, "question": "O que o contrato compra?"}
NEWS = {"kinds": ["noticiar"], "promise": PROMISE, "event_date": "2026-10-01"}
THESIS = {"thesis": "Isso deveria ter licitação.", "thesis_by": "dono"}
OPINION = {"kinds": ["opinar"], "promise": PROMISE, **THESIS}


def manifest(objective: dict[str, Any] | None) -> ScenesManifest:
    scene = {"id": "S01", "narration": "Uma fala.", "visual_need": "contextual_stock", "search_query": "x"}
    raw: dict[str, Any] = {"episode_id": "ep", "language": "pt-BR", "scenes": [scene]}
    if objective is not None:
        raw["objective"] = objective
    return ScenesManifest.model_validate(raw)


def test_each_kind_asks_for_its_own_fields() -> None:
    assert Objective.model_validate(EXPLAIN).main == "explicar"
    assert Objective.model_validate(NEWS).event_date == date(2026, 10, 1)
    assert Objective.model_validate(OPINION).thesis_by == "dono"
    for kind, missing in (("explicar", "question"), ("noticiar", "event_date"), ("opinar", "thesis")):
        with pytest.raises(ValidationError, match=f"objetivo {kind} precisa de {missing}"):
            Objective.model_validate({"kinds": [kind], "promise": PROMISE})
    with pytest.raises(ValidationError, match="precisa de thesis_by"):  # opinião sem dono não entra
        Objective.model_validate({"kinds": ["opinar"], "promise": PROMISE, "thesis": "Acho que sim."})


def test_a_video_can_combine_kinds_in_the_order_they_appear() -> None:
    combined = Objective.model_validate({
        "kinds": ["noticiar", "explicar", "opinar"], "promise": PROMISE, "event_date": "2026-10-01",
        "question": "O que o contrato compra?", "thesis": "Isso deveria ter licitação.", "thesis_by": "dono",
    })
    assert combined.main == "noticiar"  # o primeiro manda na estrutura
    with pytest.raises(ValidationError, match="tipos de objetivo"):
        Objective.model_validate({**EXPLAIN, "kinds": ["explicar", "explicar"]})
    with pytest.raises(ValidationError):
        Objective.model_validate({**EXPLAIN, "kinds": []})
    with pytest.raises(ValidationError):
        Objective.model_validate({**EXPLAIN, "kinds": ["ensinar"]})


def test_a_field_only_exists_with_its_kind() -> None:
    with pytest.raises(ValidationError, match="thesis só existe com o objetivo opinar"):
        Objective.model_validate({**EXPLAIN, "thesis": "Acho que sim."})
    with pytest.raises(ValidationError, match="event_date só existe com o objetivo noticiar"):
        Objective.model_validate({**EXPLAIN, "event_date": "2026-10-01"})


def test_question_is_a_question_and_promise_is_required() -> None:
    with pytest.raises(ValidationError, match="termina com"):
        Objective.model_validate({**EXPLAIN, "question": "O contrato."})
    with pytest.raises(ValidationError):
        Objective.model_validate({"kinds": ["explicar"], "question": "O que é?"})


def test_script_without_an_objective_warns_and_old_scripts_still_load() -> None:
    assert manifest(None).objective is None  # roteiros antigos continuam válidos
    (warning,) = objective_warnings(manifest(None))
    assert "sem objetivo declarado" in warning
    assert objective_warnings(manifest(EXPLAIN)) == []


def test_old_news_is_not_news() -> None:
    fresh = date(2026, 10, 1 + NEWS_MAX_AGE_DAYS)
    assert objective_warnings(manifest(NEWS), today=fresh) == []
    (old,) = objective_warnings(manifest(NEWS), today=date(2026, 12, 1))
    assert "fato é de 01/10/2026 (61 dias)" in old and "explica ou opina" in old
    (future,) = objective_warnings(manifest(NEWS), today=date(2026, 9, 1))
    assert "data no futuro" in future
    assert objective_warnings(manifest(NEWS)) == []  # sem a data de hoje, não confere


def test_summary_line_shows_what_the_video_promises() -> None:
    assert objective_summary(manifest(None)) is None
    assert objective_summary(manifest(EXPLAIN)) == f"objetivo: explicar: {PROMISE}"
    both = {**NEWS, "kinds": ["noticiar", "explicar"], "question": "O que o contrato compra?"}
    assert objective_summary(manifest(both)) == f"objetivo: noticiar + explicar: {PROMISE}"
