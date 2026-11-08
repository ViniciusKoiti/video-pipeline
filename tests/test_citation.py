"""Emenda de citação (ADR 007): quadro parado de obra, só de material oficial, com limites no `vp check`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from app.pipeline.check import check_episode
from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.schemas import Asset, Shot, citation_violations
from tests.test_research import EP, episode, facts_file, scenes
from tests.test_schemas import commons_asset

SHOT = TypeAdapter(Shot)


def citation(asset_id: str = "dn-quadro-01", **changes: Any) -> dict[str, Any]:
    defaults = {
        "id": asset_id,
        "provider": "official",
        "provider_id": "viz-youtube-ep01-00412",
        "page_url": "https://example.org/oficial/episodio-01",
        "license_id": "Citacao",
        "author": None,
        "work": "Death Note (2006), Madhouse; © D.N. Dream Partners, VAP, Shueisha, Madhouse, NTV",
        "attribution_text": "Death Note (2006), Madhouse",
        "usage_notes": "Ilustra o trecho 'decide julgar sozinho': a cena em que a decisão é tomada.",
    }
    return commons_asset(**{**defaults, **changes})


def test_citation_frame_is_approved_with_work_credit_and_justification() -> None:
    assert Asset.model_validate(citation()).license_id == "Citacao"


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"work": " "}, "citação exige work"),
        ({"attribution_text": ""}, "citação exige attribution_text"),
        ({"usage_notes": ""}, "citação exige usage_notes"),
        ({"page_url": None}, "page_url"),
        ({"provider": "wikimedia_commons"}, "material oficial público"),
    ],
)
def test_citation_approval_requires_its_fields(changes: dict[str, Any], message: str) -> None:
    Asset.model_validate(citation(review_status="needs_review", **changes))
    with pytest.raises(ValidationError, match=message):
        Asset.model_validate(citation(**changes))


def test_official_material_only_enters_as_citation() -> None:
    with pytest.raises(ValidationError, match="material oficial público"):
        Asset.model_validate(citation(license_id="CC0-1.0"))


def media(kind: str, asset_id: str) -> Shot:
    shot = {"kind": kind, "anchor": "x", "visual_need": "historical_exact", "search_query": "q"}
    return SHOT.validate_python({**shot, "asset_id": asset_id})


def photo(asset_id: str) -> Shot:
    return media("photo", asset_id)


def test_citation_limits_frames_and_screen_time() -> None:
    assets = {
        f"q{i}": Asset.model_validate(citation(f"q{i}"))
        for i in range(SchemasConstants.MAX_CITATION_FRAMES + 1)
    }
    within = [("S01", photo(f"q{i}"), 4000) for i in range(SchemasConstants.MAX_CITATION_FRAMES)]
    assert citation_violations(within, assets) == []
    over = [*within, ("S02", photo(f"q{SchemasConstants.MAX_CITATION_FRAMES}"), 4000)]
    assert citation_violations(over, assets) == [
        (
        f'{SchemasConstants.MAX_CITATION_FRAMES + 1} quadros citados no vídeo (máximo '
        f'{SchemasConstants.MAX_CITATION_FRAMES})'
    )
    ]
    assert citation_violations([("S01", photo("q0"), 9500)], assets) == [
        "S01: citação q0 com ~9.5 s na tela (máximo 8 s)"
    ]


def test_still_citation_never_goes_in_broll() -> None:
    broll = media("broll", "q0")
    assets = {"q0": Asset.model_validate(citation("q0"))}
    assert citation_violations([("S01", broll, 3000)], assets) == [
        "S01: citação q0 é quadro parado e não vai em B-roll"
    ]


def clip(asset_id: str = "c0", **changes: Any) -> dict[str, Any]:
    defaults = {
        "provider": "owner_capture",
        "page_url": None,
        "media": "clip",
        "origin": "captura do dono, episódio 01",
        "timecode": "00:12:03-00:12:08",
    }
    return citation(asset_id, **{**defaults, **changes})


def test_clip_needs_origin_timecode_and_citation_license() -> None:
    assert Asset.model_validate(clip()).media == "clip"
    for changes, message in [
        ({"origin": " "}, "clipe exige origin"),
        ({"timecode": None}, "clipe exige origin"),
        ({"license_id": "CC0-1.0", "provider": "pexels"}, "clipe só na licença Citacao"),
        ({"media": "still"}, "captura do dono só vale para clipe"),
    ]:
        with pytest.raises(ValidationError, match=message):
            Asset.model_validate(clip(**changes))


def test_clip_has_no_numeric_cap_but_only_goes_in_broll() -> None:
    assets = {f"c{i}": Asset.model_validate(clip(f"c{i}")) for i in range(30)}
    many = [("S01", media("broll", f"c{i}"), 20000) for i in range(30)]
    assert citation_violations(many, assets) == []
    assert citation_violations([("S01", photo("c0"), 3000)], assets) == [
        "S01: citação c0 é clipe e só vai em B-roll"
    ]


def test_other_licenses_are_not_counted() -> None:
    assets = {"c": Asset.model_validate(commons_asset(id="c"))}
    assert citation_violations([("S01", photo("c"), 20000)], assets) == []


def test_vp_check_reads_the_chosen_assets(tmp_path: Path) -> None:
    raw = scenes()
    raw["scenes"][0]["shots"][1]["asset_id"] = "dn-quadro-01"
    raw["scenes"][0]["shots"][1]["visual_need"] = "historical_exact"
    store = episode(tmp_path, facts=facts_file(), scenes_json=raw)
    assets_dir = tmp_path / "episodes" / EP / "assets"
    assets_dir.mkdir()
    (assets_dir / "dn-quadro-01.json").write_text(json.dumps(citation(), ensure_ascii=False))
    report = check_episode(store, EP, chars_per_second=2.0)  # narração lenta: o plano passa de 8 s
    assert any("citação dn-quadro-01 com ~" in e for e in report.errors)
    assert not check_episode(store, EP).errors
