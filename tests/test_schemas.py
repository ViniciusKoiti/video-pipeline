import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from app.pipeline.schemas import (
    Asset,
    Claim,
    EpisodeManifest,
    ReviewLog,
    ScenesManifest,
    SourcesManifest,
    Step,
    VideoSpec,
    VisualNeed,
    unknown_source_refs,
    visual_need_violations,
)

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "pilot-example"


def load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE / name).read_text())


def fixture_assets() -> dict[str, Asset]:
    assets = [Asset.model_validate_json(p.read_text()) for p in sorted((FIXTURE / "assets").glob("*.json"))]
    return {a.id: a for a in assets}


# --- Fixture ------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "model"),
    [
        ("sources.json", SourcesManifest),
        ("scenes.json", ScenesManifest),
        ("review.json", ReviewLog),
        ("episode.json", EpisodeManifest),
        ("assets/example-commons-001.json", Asset),
        ("assets/original-map-001.json", Asset),
        ("assets/workers-ai-001.json", Asset),
    ],
)
def test_fixture_validates_and_round_trips(name: str, model: type[BaseModel]) -> None:
    raw = load(name)
    parsed = model.model_validate(raw)
    assert model.model_validate_json(parsed.model_dump_json()) == parsed


def test_fixture_is_consistent_across_files() -> None:
    scenes = ScenesManifest.model_validate(load("scenes.json"))
    sources = SourcesManifest.model_validate(load("sources.json"))
    assert unknown_source_refs(scenes, sources) == []
    assert visual_need_violations(scenes, fixture_assets()) == []
    for scene in scenes.scenes:
        assert scene.chosen_asset_id in fixture_assets()
    for path in (s.local_path for s in sources.sources):
        assert (FIXTURE / path).is_file()


def test_fixture_episode_timeline() -> None:
    episode = EpisodeManifest.model_validate(load("episode.json"))
    scenes = ScenesManifest.model_validate(load("scenes.json"))
    assert episode.duration_ms == sum(s.duration_ms or 0 for s in scenes.scenes) == 14_900
    assert fixture_assets()["workers-ai-001"].is_synthetic


def test_extra_fields_are_rejected() -> None:
    raw = load("sources.json")
    raw["sources"][0]["unexpected"] = 1
    with pytest.raises(ValidationError, match="unexpected"):
        SourcesManifest.model_validate(raw)


# --- Claims e cenas (§2.2) ----------------------------------------------------------------------


def test_claim_without_source_ids_is_rejected() -> None:
    with pytest.raises(ValidationError, match="source_ids"):
        Claim(text="Departure date", source_ids=[])


def test_claim_excerpt_must_come_from_listed_source() -> None:
    with pytest.raises(ValidationError, match="source-02#E1"):
        Claim(text="Departure date", source_ids=["source-01"], excerpt_ids=["source-02#E1"])


def test_unknown_source_is_reported() -> None:
    raw = load("scenes.json")
    raw["scenes"][0]["claims"][0]["source_ids"].append("source-09")
    problems = unknown_source_refs(
        ScenesManifest.model_validate(raw), SourcesManifest.model_validate(load("sources.json"))
    )
    assert problems == ["S01: fonte source-09 não está em sources.json"]


def test_visual_need_has_exactly_four_values() -> None:
    assert {v.value for v in VisualNeed} == {
        "historical_exact",
        "contextual_stock",
        "map_or_graphic",
        "illustrative_reconstruction",
    }
    raw = load("scenes.json")
    raw["scenes"][0]["visual_need"] = "photo"
    with pytest.raises(ValidationError, match="visual_need"):
        ScenesManifest.model_validate(raw)


def test_duplicate_scene_ids_are_rejected() -> None:
    raw = load("scenes.json")
    raw["scenes"][1]["id"] = "S01"
    with pytest.raises(ValidationError, match="duplicados: S01"):
        ScenesManifest.model_validate(raw)


def test_generated_image_cannot_be_historical_record() -> None:
    raw = load("scenes.json")
    raw["scenes"][2]["visual_need"] = "historical_exact"
    problems = visual_need_violations(ScenesManifest.model_validate(raw), fixture_assets())
    assert problems == ["S03: historical_exact não pode usar workers_ai"]


# --- Ativos e licenças (§2.3, ADR 007) ----------------------------------------------------------


def commons_asset(**changes: Any) -> dict[str, Any]:
    return {**load("assets/example-commons-001.json"), **changes}


def test_asset_without_license_can_exist_but_not_be_approved() -> None:
    pending = Asset.model_validate(commons_asset(license_id=None, review_status="needs_review"))
    assert pending.license_id is None
    with pytest.raises(ValidationError, match="fora da lista aceita"):
        Asset.model_validate(commons_asset(license_id=None))


@pytest.mark.parametrize("license_id", ["CC-BY-SA-4.0", "CC-BY-NC-4.0", "All rights reserved"])
def test_licenses_outside_the_list_block_approval(license_id: str) -> None:
    with pytest.raises(ValidationError, match="fora da lista aceita"):
        Asset.model_validate(commons_asset(license_id=license_id))


def test_public_domain_requires_reasoning() -> None:
    with pytest.raises(ValidationError, match="usage_notes"):
        Asset.model_validate(commons_asset(usage_notes=" "))


def test_cc_by_3_br_is_accepted_with_attribution() -> None:
    asset = Asset.model_validate(
        commons_asset(
            license_id="CC-BY-3.0-BR",
            author="Antônio Cruz/ABr",
            attribution_text="Antônio Cruz/Agência Brasil, CC BY 3.0 BR",
        )
    )
    assert asset.license_id == "CC-BY-3.0-BR"
    with pytest.raises(ValidationError, match="attribution_text"):
        Asset.model_validate(commons_asset(license_id="CC-BY-3.0-BR", attribution_text=""))


def test_cc_by_requires_attribution() -> None:
    with pytest.raises(ValidationError, match="attribution_text"):
        Asset.model_validate(commons_asset(license_id="CC-BY-4.0", attribution_text=""))


def test_approval_requires_downloaded_file() -> None:
    with pytest.raises(ValidationError, match="sha256"):
        Asset.model_validate(commons_asset(sha256=None))


def test_generated_image_requires_generation_metadata() -> None:
    raw = load("assets/workers-ai-001.json")
    del raw["generation"]
    with pytest.raises(ValidationError, match="generation"):
        Asset.model_validate(raw)
    with pytest.raises(ValidationError, match="generation"):
        Asset.model_validate(commons_asset(generation=load("assets/workers-ai-001.json")["generation"]))


# --- review.json (§5) ---------------------------------------------------------------------------


def test_latest_review_decision_wins() -> None:
    review = ReviewLog.model_validate(load("review.json"))
    assert review.is_approved(Step.SCRIPT)
    assert review.is_approved(Step.SCRIPT, input_hash="sha256:script-v2")
    assert not review.is_approved(Step.SCRIPT, input_hash="sha256:script-v1")  # conteúdo mudou
    assert review.is_approved(Step.ASSETS, asset_id="workers-ai-001")
    assert review.is_approved(Step.PREVIEW, scene_id="S03")
    assert not review.is_approved(Step.PREVIEW)  # a prévia inteira ainda não foi aprovada
    assert not review.is_approved(Step.VOICE)


def test_review_entry_has_single_target() -> None:
    raw = load("review.json")
    raw["entries"][0] |= {"scene_id": "S01", "asset_id": "original-map-001"}
    with pytest.raises(ValidationError, match="não ambos"):
        ReviewLog.model_validate(raw)


# --- episode.json -------------------------------------------------------------------------------


def test_overlapping_scenes_are_rejected() -> None:
    raw = load("episode.json")
    raw["scenes"][1]["start_ms"] = 6000
    with pytest.raises(ValidationError, match="S02 começa antes do fim de S01"):
        EpisodeManifest.model_validate(raw)


@pytest.mark.parametrize("path", ["/tmp/S01.wav", "../other/S01.wav", "voice\\S01.wav"])
def test_media_paths_must_stay_inside_episode(path: str) -> None:
    raw = load("episode.json")
    raw["scenes"][0]["audio"] = path
    with pytest.raises(ValidationError, match="relativo"):
        EpisodeManifest.model_validate(raw)


def test_video_must_be_16_by_9() -> None:
    assert VideoSpec() == VideoSpec(width=1920, height=1080, fps=30, audio_sample_rate=48_000)
    with pytest.raises(ValidationError, match="16:9"):
        VideoSpec(width=1080, height=1920)
