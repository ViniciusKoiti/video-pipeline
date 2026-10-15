"""Estágio do funil (ADR 026): topo, meio e fundo, com a chamada final e, no fundo, a oferta."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from app.pipeline.check import funnel_summary, funnel_warnings
from app.pipeline.schemas import Funnel, ScenesManifest

LAST = "A conta é preço dividido pelo peso. Salva pra conferir na próxima encomenda."
MIDDLE = {"stage": "meio", "cta": "Salva pra conferir na próxima encomenda."}
OFFER = "planilha de custo por unidade"
BOTTOM = {"stage": "fundo", "cta": "Comenta PLANILHA que eu te mando.", "offer": OFFER}


def manifest(funnel: dict[str, Any] | None, last: str = LAST) -> ScenesManifest:
    scenes = [
        {"id": "S01", "narration": "Uma fala.", "visual_need": "contextual_stock", "search_query": "x"},
        {"id": "S02", "narration": last, "visual_need": "contextual_stock", "search_query": "x"},
    ]
    raw: dict[str, Any] = {"episode_id": "ep", "language": "pt-BR", "scenes": scenes}
    if funnel is not None:
        raw["funnel"] = funnel
    return ScenesManifest.model_validate(raw)


def test_each_stage_and_the_offer_only_at_the_bottom() -> None:
    assert Funnel.model_validate(MIDDLE).stage == "meio"
    assert Funnel.model_validate(BOTTOM).offer == OFFER
    with pytest.raises(ValidationError, match="funil fundo precisa de offer"):
        Funnel.model_validate({**BOTTOM, "offer": None})
    with pytest.raises(ValidationError, match="offer só existe no funil fundo"):
        Funnel.model_validate({**MIDDLE, "offer": "planilha"})
    with pytest.raises(ValidationError):
        Funnel.model_validate({**MIDDLE, "stage": "lateral"})
    with pytest.raises(ValidationError):
        Funnel.model_validate({"stage": "topo"})  # sem chamada não entra


def test_script_without_a_stage_warns_and_old_scripts_still_load() -> None:
    assert manifest(None).funnel is None  # roteiros antigos continuam válidos
    (warning,) = funnel_warnings(manifest(None))
    assert "sem estágio do funil" in warning
    assert funnel_warnings(manifest(MIDDLE)) == []


def test_the_call_asks_what_the_stage_asks() -> None:
    saves = "Salva pra conferir."
    (wrong,) = funnel_warnings(manifest({"stage": "topo", "cta": saves}, saves))
    assert "funil topo" in wrong and "seguir ou compartilhar" in wrong
    follow = "Segue pra ver a próxima."
    assert funnel_warnings(manifest({"stage": "topo", "cta": follow}, follow)) == []
    bottom = manifest(BOTTOM, "Quer a planilha pronta? Comenta PLANILHA que eu te mando.")
    assert funnel_warnings(bottom) == []


def test_the_call_is_said_in_the_last_scene() -> None:
    (missing,) = funnel_warnings(manifest(MIDDLE, "A conta é preço dividido pelo peso."))
    assert "não está na narração da última cena (S02)" in missing
    # acentos, maiúsculas, pontuação e marcas de pausa não contam como diferença
    assert funnel_warnings(manifest(MIDDLE, "Salva <short pause> pra CONFERIR na proxima encomenda!")) == []


def test_summary_line_shows_stage_call_and_offer() -> None:
    assert funnel_summary(manifest(None)) is None
    assert funnel_summary(manifest(MIDDLE)) == f"funil: meio; chamada: {MIDDLE['cta']}"
    line = funnel_summary(manifest(BOTTOM, "Comenta PLANILHA que eu te mando."))
    assert line is not None and line.endswith(f"; oferta: {OFFER}")
