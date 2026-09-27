"""Adapters de banco de imagem (§8, ADR 007): filtros, cache, cota e segredos, sem rede (§2.10)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.pipeline.schemas import Provider, Status, VisualNeed
from app.providers.archives.base import AssetQuery
from app.providers.archives.pexels import PexelsArchive
from app.providers.archives.stock import normalize_query, sha256_file
from app.providers.errors import ProviderError, QuotaExhausted
from app.providers.http import TransportError
from tests.fakes import FIXED_TIME, FakeHttp

FIXTURES = Path(__file__).parent / "fixtures" / "archives"
KEY = "chave-secreta-de-teste"
QUOTA = {"x-ratelimit-limit": "20000", "x-ratelimit-remaining": "19684", "x-ratelimit-reset": "1590529646"}


def recorded(provider: str, name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / provider / name).read_text())


def pexels(cache_dir: Path | None = None, **routes: Any) -> tuple[PexelsArchive, FakeHttp]:
    http = FakeHttp(
        routes
        or {
            "/videos/search": recorded("pexels", "videos-search.json"),
            "/v1/search": recorded("pexels", "photos-search.json"),
        },
        headers={"content-type": "application/json", "set-cookie": "sessao=1", **QUOTA},
    )
    archive = PexelsArchive(
        KEY, cache_dir=cache_dir, get=http.get, get_file=http.get_file, now=lambda: FIXED_TIME
    )
    return archive, http


def video_query(text: str = "Saco de cimento", **changes: Any) -> AssetQuery:
    return AssetQuery(text=text, visual_need=VisualNeed.CONTEXTUAL_STOCK, media="video", **changes)


def test_normalized_query_ignores_case_and_spacing() -> None:
    assert normalize_query("  Saco  de\tCIMENTO ") == "saco de cimento"


def test_pexels_video_keeps_landscape_1080p_files_long_enough() -> None:
    archive, http = pexels()
    [candidate] = archive.search_assets(video_query(min_duration_s=5))
    asset = candidate.asset
    assert asset.id == "pexels-video-1448735"  # o vertical (2499611) e o curto (900001) ficam de fora
    assert (candidate.width, candidate.height, candidate.duration_s) == (
        2048,
        1080,
        32,
    )  # menor arquivo ≥ 1080p
    assert "profile_id=175" in (asset.original_url or "")
    assert (asset.provider, asset.license_id, asset.author) == (Provider.PEXELS, "Pexels", "Ruvim Miksanskiy")
    assert asset.attribution_text == "Ruvim Miksanskiy via Pexels"
    assert asset.page_url == "https://www.pexels.com/video/video-of-forest-1448735/"
    assert asset.review_status is Status.NEEDS_REVIEW  # conferência de pessoas e marcas é humana
    url, headers = http.calls[0]
    assert url.startswith(
        "https://api.pexels.com/v1/videos/search?query=saco+de+cimento&orientation=landscape"
    )
    assert headers == {"Authorization": KEY}


def test_pexels_without_min_duration_respects_limit() -> None:
    archive, _ = pexels()
    candidates = archive.search_assets(video_query(limit=2))
    assert [c.asset.id for c in candidates] == ["pexels-video-1448735", "pexels-video-900001"]


def test_pexels_photo_must_be_landscape_and_at_least_1920() -> None:
    archive, _ = pexels()
    query = AssetQuery(text="farmácia", visual_need=VisualNeed.CONTEXTUAL_STOCK)
    [candidate] = archive.search_assets(query)  # a vertical (3573351) e a quadrada (2014422) ficam de fora
    assert candidate.asset.id == "pexels-photo-900002"
    assert candidate.asset.original_url == "https://images.pexels.com/photos/900002/pexels-photo-900002.jpeg"
    assert candidate.duration_s is None


def test_pexels_search_is_cached_with_quota_and_without_the_key(tmp_path: Path) -> None:
    archive, http = pexels(tmp_path)
    first = archive.search_assets(video_query("Saco de cimento", limit=2))
    again = archive.search_assets(video_query("  saco DE cimento ", limit=2))
    api_calls = [url for url, _ in http.calls if url.startswith("https://api.pexels.com")]
    assert len(api_calls) == 1  # a segunda busca vem do cache
    assert [c.asset.id for c in again] == [c.asset.id for c in first]
    assert all(c.thumbnail_path and c.thumbnail_path.is_file() for c in again)
    files = [p for p in (tmp_path / "pexels").rglob("*") if p.is_file()]
    assert all(KEY not in p.read_text(errors="ignore") for p in files)
    quota = json.loads((tmp_path / "pexels" / "quota.json").read_text())
    assert quota["headers"] == QUOTA  # só os headers de cota, nada de cookie


def test_pexels_download_goes_without_the_key(tmp_path: Path) -> None:
    archive, http = pexels()
    [candidate] = archive.search_assets(video_query(min_duration_s=5))
    dest = archive.download_asset(candidate.asset, tmp_path / "assets" / "a.mp4")
    assert len(sha256_file(dest)) == 64
    url, headers = http.calls[-1]
    assert url == candidate.asset.original_url and headers == {}


@pytest.mark.parametrize(
    ("status", "error"), [(429, QuotaExhausted), (401, ProviderError), (500, ProviderError)]
)
def test_pexels_errors_stop_the_scene_without_leaking_the_key(
    status: int, error: type[ProviderError]
) -> None:
    archive, _ = pexels(**{"/videos/search": TransportError(status, "falhou")})
    with pytest.raises(error) as raised:
        archive.search_assets(video_query())
    assert KEY not in str(raised.value) and "api.pexels.com" not in str(raised.value)
