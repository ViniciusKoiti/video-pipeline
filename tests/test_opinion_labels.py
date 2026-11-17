"""Opinião dita sem rótulo (ADR 019, emenda de 2026-11-16)."""

from __future__ import annotations

from typing import Any

import pytest

from app.pipeline.opinion_labels import opinion_label_errors
from app.pipeline.schemas import ScenesManifest


def manifest(*narrations: str) -> ScenesManifest:
    scenes: list[dict[str, Any]] = [
        {"id": f"S0{i}", "narration": text, "visual_need": "contextual_stock", "search_query": "x"}
        for i, text in enumerate(narrations, start=1)
    ]
    return ScenesManifest.model_validate({"episode_id": "ep", "language": "pt-BR", "scenes": scenes})


@pytest.mark.parametrize("label", [
    "Se essa noite parece familiar, fico do seu lado. E eu digo o que acho disso, como opinião.",
    "Digo isso como opinião, não como fato.",
    "Isso é só uma opinião minha.",
    "É uma opinião pessoal: o vazio avisa.",
    "Isso é opinião do canal.",
    "I say this as an opinion.",
])
def test_a_label_that_announces_the_opinion_is_an_error(label: str) -> None:
    (error,) = opinion_label_errors(manifest("Uma fala.", label))
    assert error.startswith("S02: rótulo de opinião") and "na minha leitura" in error


@pytest.mark.parametrize("natural", [
    "Na minha leitura, o vazio é um aviso.",
    "Pelo menos é assim que eu enxergo.",
    "Eu acho que o problema começa quando a gente mora na anestesia.",
    "Na minha opinião, o caderno ajuda.",
    "Ela mudou a opinião pública da cidade.",
    "Como opinião pública, isso pesou.",
])
def test_natural_opinion_passes(natural: str) -> None:
    assert opinion_label_errors(manifest(natural)) == []


def test_the_label_is_quoted_from_the_script_with_accents() -> None:
    (error,) = opinion_label_errors(manifest("E eu digo o que acho <short pause> disso, como opinião."))
    assert "'como opinião'" in error
