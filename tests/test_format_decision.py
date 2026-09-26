"""Tomador de decisão da modalidade (ADR 001): recomenda; o humano confirma ou troca."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.pipeline.format_decision import (
    FormatDecision,
    FormatNotConfirmed,
    TopicAssessment,
    TopicKind,
    confirmed_format,
    decide_from_scenes,
    decide_from_topic,
)
from app.pipeline.schemas import EpisodeFormat, ReviewEntry, ReviewLog, ScenesManifest

NOW = datetime(2026, 9, 26, 12, 0, tzinfo=UTC)
ENGINE_TEST = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"
DOC, EXPLAINER = EpisodeFormat.ARCHIVAL_DOCUMENTARY, EpisodeFormat.EXPLAINER


def engine_test_scenes() -> ScenesManifest:
    return ScenesManifest.model_validate_json((ENGINE_TEST / "scenes.json").read_text())


def with_needs(*needs: str) -> ScenesManifest:
    """Cenas sintéticas, validadas (model_copy não valida e deixaria visual_need como texto cru)."""
    template = engine_test_scenes().scenes[0].model_dump(mode="json")
    scenes = [
        {**template, "id": f"S{i:02d}", "visual_need": need, "claims": []} for i, need in enumerate(needs, 1)
    ]
    return ScenesManifest.model_validate({"episode_id": "engine-test", "language": "en", "scenes": scenes})


# --- Pelo tema (vp new) -------------------------------------------------------------------------


def test_historical_event_before_1930_is_a_documentary() -> None:
    decision = decide_from_topic(TopicAssessment(kind=TopicKind.HISTORICAL_EVENT, period_year=1884), now=NOW)
    assert decision.recommended is DOC and decision.scores[DOC] == 0.9
    assert any("domínio público" in reason for reason in decision.reasons)


def test_recent_event_loses_confidence_for_lack_of_public_domain_photos() -> None:
    decision = decide_from_topic(TopicAssessment(kind=TopicKind.HISTORICAL_EVENT, period_year=1996), now=NOW)
    assert decision.recommended is EXPLAINER and decision.scores[DOC] == 0.45
    assert any("§1" in reason for reason in decision.reasons)


def test_concept_is_an_explainer_and_unclear_falls_back_to_mvp() -> None:
    concept = decide_from_topic(TopicAssessment(kind=TopicKind.CONCEPT), now=NOW)
    unclear = decide_from_topic(TopicAssessment(kind=TopicKind.UNCLEAR), now=NOW)
    assert concept.recommended is EXPLAINER
    assert unclear.recommended is DOC and unclear.scores == {DOC: 0.5, EXPLAINER: 0.5}


# --- Pelas cenas (vp scenes) --------------------------------------------------------------------


def test_engine_test_is_a_documentary_with_one_graphic_as_asset() -> None:
    decision = decide_from_scenes(engine_test_scenes(), now=NOW)
    assert decision.stage == "scenes" and decision.recommended is DOC
    assert decision.graphic_scenes_as_assets == ["S03"]  # linha do tempo 1882–1883
    assert decision.reasons[:2] == [
        "4 de 5 planos pedem foto (historical_exact/contextual_stock)",
        "1 de 5 planos são gráficos (número, gráfico, mapa, citação...): 20%",
    ]


def test_mostly_graphic_scenes_make_an_explainer() -> None:
    decision = decide_from_scenes(
        with_needs(
            "map_or_graphic", "map_or_graphic", "map_or_graphic", "contextual_stock", "map_or_graphic"
        ),
        now=NOW,
    )
    assert decision.recommended is EXPLAINER and decision.graphic_scenes_as_assets == []


# --- Confirmação humana (§2.5) ------------------------------------------------------------------


def review_of(recommendation: FormatDecision, **entry: object) -> ReviewLog:
    fields = {
        "step": "format",
        "decision": "approved",
        "reviewer": "Vinicius Koiti",
        "at": NOW,
        "input_hash": recommendation.input_hash,
        **entry,
    }
    return ReviewLog(episode_id="engine-test", entries=[ReviewEntry(**fields)])


def test_format_needs_human_confirmation() -> None:
    decision = decide_from_scenes(engine_test_scenes(), now=NOW)
    with pytest.raises(FormatNotConfirmed, match="não confirmada"):
        confirmed_format(decision, ReviewLog(episode_id="engine-test"))
    assert confirmed_format(decision, review_of(decision)) is DOC


def test_human_can_override_the_recommendation() -> None:
    decision = decide_from_scenes(engine_test_scenes(), now=NOW)
    review = review_of(decision, decision="changes_requested", choice="explainer", notes="quero animar tudo")
    assert confirmed_format(decision, review) is EXPLAINER


def test_confirmation_expires_when_scenes_change() -> None:
    approved = decide_from_scenes(engine_test_scenes(), now=NOW)
    changed = decide_from_scenes(with_needs("historical_exact", "historical_exact"), now=NOW)
    with pytest.raises(FormatNotConfirmed):
        confirmed_format(changed, review_of(approved))
