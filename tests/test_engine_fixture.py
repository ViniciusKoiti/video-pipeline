"""Fixture `engine-test` (etapa 6): entrada idêntica para o experimento de motor."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel

from app.media.probe import duration_ms
from app.pipeline.schemas import (
    APPROVED_STATES,
    Asset,
    EpisodeManifest,
    ReviewLog,
    ScenesManifest,
    SourcesManifest,
    Step,
    unknown_source_refs,
    visual_need_violations,
)

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"
SRT_TIME = r"(\d\d):(\d\d):(\d\d),(\d\d\d)"
M = TypeVar("M", bound=BaseModel)


def load(name: str, model: type[M]) -> M:
    return model.model_validate_json((FIXTURE / name).read_text())


@pytest.fixture(scope="module")
def episode() -> EpisodeManifest:
    return load("episode.json", EpisodeManifest)


@pytest.fixture(scope="module")
def scenes() -> ScenesManifest:
    return load("scenes.json", ScenesManifest)


@pytest.fixture(scope="module")
def assets() -> dict[str, Asset]:
    parsed = [Asset.model_validate_json(p.read_text()) for p in sorted((FIXTURE / "assets").glob("*.json"))]
    return {a.id: a for a in parsed}


def test_claims_cite_real_excerpts(scenes: ScenesManifest) -> None:
    sources = load("sources.json", SourcesManifest)
    assert unknown_source_refs(scenes, sources) == []
    texts = {s.id: (FIXTURE / s.local_path).read_text() for s in sources.sources}
    for scene in scenes.scenes:
        assert scene.claims, f"{scene.id} sem claims"
        for claim in scene.claims:
            assert claim.excerpt_ids, f"{scene.id}: claim sem trecho"
            for excerpt in claim.excerpt_ids:
                source_id, number = excerpt.split("#")
                assert f"[{number}]" in texts[source_id], f"{excerpt} não existe em {source_id}"


def test_every_asset_is_approved_with_matching_file(
    assets: dict[str, Asset], episode: EpisodeManifest
) -> None:
    review = load("review.json", ReviewLog)
    files = {s.asset_id: FIXTURE / s.image for s in episode.scenes}
    assert set(files) == set(assets)
    for asset_id, path in files.items():
        asset = assets[asset_id]
        assert asset.review_status in APPROVED_STATES
        assert hashlib.sha256(path.read_bytes()).hexdigest() == asset.sha256
        assert review.is_approved(Step.ASSETS, asset_id=asset_id, input_hash=f"sha256:{asset.sha256}")


def test_visual_needs_fit_the_assets(scenes: ScenesManifest, assets: dict[str, Asset]) -> None:
    assert visual_need_violations(scenes, assets) == []
    graphic = next(s for s in scenes.scenes if s.visual_need == "map_or_graphic")
    assert assets[graphic.chosen_asset_id or ""].license_id == "Original"


def test_timeline_comes_from_real_voice(episode: EpisodeManifest, scenes: ScenesManifest) -> None:
    assert 30_000 <= episode.duration_ms <= 60_000
    assert [s.duration_ms for s in scenes.scenes] == [s.duration_ms for s in episode.scenes]
    assert episode.scenes[0].start_ms == 0
    for previous, current in zip(episode.scenes, episode.scenes[1:], strict=False):
        assert current.start_ms == previous.end_ms  # sem buracos entre blocos
    for scene in episode.scenes:
        assert duration_ms(FIXTURE / scene.audio) == scene.duration_ms


def test_human_reviews_cover_gates_but_not_voice() -> None:
    review = load("review.json", ReviewLog)
    assert review.is_approved(Step.SOURCES) and review.is_approved(Step.SCRIPT)
    assert not review.is_approved(Step.VOICE)  # ninguém ouviu a narração ainda
    assert {e.reviewer for e in review.entries} == {"Vinicius Koiti"}


def test_captions_cover_the_narration_in_order(episode: EpisodeManifest) -> None:
    blocks = (FIXTURE / (episode.captions or "")).read_text().strip().split("\n\n")
    cues = []
    for block in blocks:
        _, timing, *text = block.splitlines()
        start, end = (
            int(h) * 3_600_000 + int(m) * 60_000 + int(s) * 1000 + int(ms)
            for h, m, s, ms in re.findall(SRT_TIME, timing)
        )
        cues.append((start, end, " ".join(text)))
    assert cues[0][0] == 0 and abs(cues[-1][1] - episode.duration_ms) <= 5
    assert all(start < end for start, end, _ in cues)
    assert all(a[1] <= b[0] for a, b in zip(cues, cues[1:], strict=False))
    assert " ".join(c[2] for c in cues).split() == " ".join(s.narration for s in episode.scenes).split()
