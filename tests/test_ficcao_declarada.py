"""Ficção histórica declarada (ADR 055, opção C): o formato dispensa claims, inclusive no fato na tela."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from app.pipeline.models.scenes_manifest import ScenesManifest
from app.pipeline.molde import claimless_statements

NARRATION = "Em 1350 você herda o castelo do seu pai. A lã da Inglaterra vende bem em Flandres."


def manifest(*, fiction: bool | None = None, claims: list[dict[str, Any]] | None = None) -> ScenesManifest:
    stamp: dict[str, Any] = {"kind": "stamp", "anchor": "Em 1350", "date": "1350", "place": "Inglaterra"}
    if claims is not None:
        stamp["claims"] = claims
    scene = {"id": "S01", "narration": NARRATION, "shots": [stamp]}
    raw: dict[str, Any] = {"episode_id": "ep", "language": "pt-BR", "scenes": [scene]}
    if fiction is not None:
        raw["fiction"] = fiction
    return ScenesManifest.model_validate(raw)


def test_fact_on_screen_without_claims_is_refused_outside_fiction() -> None:
    with pytest.raises(ValidationError, match="S01: plano stamp sem claims"):
        manifest()
    with pytest.raises(ValidationError, match="S01: plano stamp sem claims"):
        manifest(fiction=False)


def test_declared_fiction_accepts_fact_on_screen_without_claims() -> None:
    parsed = manifest(fiction=True)
    assert parsed.fiction is True
    assert parsed.scenes[0].shots[0].claims == []


def test_claims_still_satisfy_the_rule_outside_fiction() -> None:
    claim = {"text": "1350", "source_ids": ["source-01"]}
    assert manifest(claims=[claim]).scenes[0].shots[0].claims[0].text == "1350"


def test_declared_fiction_has_no_claimless_statement_warnings() -> None:
    scene = {
        "id": "S01",
        "narration": NARRATION,
        "visual_need": "illustrative_reconstruction",
        "search_query": "castelo",
    }
    raw: dict[str, Any] = {"episode_id": "ep", "language": "pt-BR", "scenes": [scene]}
    assert claimless_statements(ScenesManifest.model_validate(raw))  # sem a marca, a frase com número avisa
    assert claimless_statements(ScenesManifest.model_validate({**raw, "fiction": True})) == []
