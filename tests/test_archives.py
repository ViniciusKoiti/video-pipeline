"""Adapters de banco de imagem (§8, ADR 007): filtros, cache, cota e segredos, sem rede (§2.10)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.pipeline.schemas import Provider, Status, VisualNeed
from app.providers.archives.base import AssetQuery
from app.providers.archives.pexels import PexelsArchive
from app.providers.archives.pixabay import PixabayArchive
from app.providers.archives.stock import normalize_query, sha256_file
from app.providers.archives.unsplash import UnsplashArchive
from app.providers.errors import ProviderError, QuotaExhausted
from app.providers.http import USER_AGENT, TransportError, download, get_json
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


# --- Pixabay ------------------------------------------------------------------------------------

PIXABAY_QUOTA = {"x-ratelimit-limit": "100", "x-ratelimit-remaining": "99", "x-ratelimit-reset": "60"}


def pixabay(cache_dir: Path | None = None, **routes: Any) -> tuple[PixabayArchive, FakeHttp]:
    default_routes = {
        "/api/videos/": recorded("pixabay", "videos-search.json"),
        "pixabay.com/api/?": recorded("pixabay", "images-search.json"),
    }
    http = FakeHttp(routes or default_routes, headers=PIXABAY_QUOTA)
    options = {"cache_dir": cache_dir, "get": http.get, "get_file": http.get_file, "now": lambda: FIXED_TIME}
    return PixabayArchive(KEY, **options), http


def test_pixabay_video_takes_the_smallest_1080p_rendition() -> None:
    archive, http = pixabay()
    candidates = archive.search_assets(video_query(min_duration_s=10))
    assert [c.asset.id for c in candidates] == [
        "pixabay-video-125",
        "pixabay-video-900003",
    ]  # 900004 só tem 720p
    first, second = candidates
    assert (first.width, first.height, first.duration_s) == (1920, 1080, 12)
    assert first.asset.original_url == "https://cdn.pixabay.com/video/2015/08/08/125-135736646_large.mp4"
    assert (
        second.asset.original_url == "https://cdn.pixabay.com/video/exemplo/900003_medium.mp4"
    )  # large vazio
    assert (first.asset.license_id, first.asset.attribution_text) == (
        "Pixabay",
        "Coverr-Free-Footage via Pixabay",
    )
    url, headers = http.calls[0]
    assert url.startswith("https://pixabay.com/api/videos/?key=") and "q=saco+de+cimento" in url
    assert "min_height=1080" in url and headers == {}


def test_pixabay_duration_filter() -> None:
    archive, _ = pixabay()
    assert [c.asset.id for c in archive.search_assets(video_query(min_duration_s=15))] == [
        "pixabay-video-900003"
    ]


def test_pixabay_photo_needs_full_access_to_reach_1920() -> None:
    archive, _ = pixabay()
    query = AssetQuery(text="usina", visual_need=VisualNeed.CONTEXTUAL_STOCK)
    [candidate] = archive.search_assets(query)  # 195893: largeImageURL chega a 1280×720 e fica de fora
    assert candidate.asset.id == "pixabay-photo-900005"
    assert (candidate.width, candidate.height) == (1920, 1080)
    assert candidate.asset.original_url == "https://pixabay.com/get/exemplo900005_1920.jpg"


def test_pixabay_cache_and_quota_never_hold_the_key(tmp_path: Path) -> None:
    archive, http = pixabay(tmp_path)
    archive.search_assets(video_query())
    archive.search_assets(video_query(" SACO de  cimento"))
    assert len([u for u, _ in http.calls if u.startswith("https://pixabay.com/api/")]) == 1
    files = [p for p in (tmp_path / "pixabay").rglob("*") if p.is_file()]
    assert files and all(KEY not in p.read_text(errors="ignore") for p in files)
    assert json.loads((tmp_path / "pixabay" / "quota.json").read_text())["headers"] == PIXABAY_QUOTA


def test_pixabay_rate_limit_stops_the_scene() -> None:
    archive, _ = pixabay(**{"/api/videos/": TransportError(429, "API rate limit exceeded")})
    with pytest.raises(QuotaExhausted) as raised:
        archive.search_assets(video_query())
    assert KEY not in str(raised.value)


# --- Unsplash -----------------------------------------------------------------------------------


def unsplash(cache_dir: Path | None = None, **routes: Any) -> tuple[UnsplashArchive, FakeHttp]:
    default_routes = {
        "/search/photos": recorded("unsplash", "search-photos.json"),
        "/download": {"url": "https://image.unsplash.com/example"},
    }
    http = FakeHttp(
        routes or default_routes, headers={"x-ratelimit-limit": "50", "x-ratelimit-remaining": "49"}
    )
    options = {"cache_dir": cache_dir, "get": http.get, "get_file": http.get_file, "now": lambda: FIXED_TIME}
    return UnsplashArchive(KEY, app_name="video_pipeline", **options), http


def photo_query(text: str = "power plant", **changes: Any) -> AssetQuery:
    return AssetQuery(text=text, visual_need=VisualNeed.CONTEXTUAL_STOCK, **changes)


def test_unsplash_photo_with_credit_links() -> None:
    archive, http = unsplash()
    [candidate] = archive.search_assets(photo_query())  # a vertical sintética fica de fora
    asset = candidate.asset
    assert (asset.id, asset.provider_id) == ("unsplash-photo-eolpjytrbsq", "eOLpJytrbsQ")
    assert asset.original_url and asset.original_url.startswith(
        "https://images.unsplash.com/photo-1416339306562-f3d12fefd36f?ixid="
    )
    assert asset.license_id == "Unsplash" and asset.author == "Jeff Sheldon"
    assert asset.attribution_text == (
        "Photo by Jeff Sheldon on Unsplash (http://unsplash.com/@ugmonk?utm_source=video_pipeline&utm_medium=referral"
        " · https://unsplash.com/?utm_source=video_pipeline&utm_medium=referral)"
    )
    url, headers = http.calls[0]
    assert url.startswith("https://api.unsplash.com/search/photos?query=power+plant&orientation=landscape")
    assert "content_filter=high" in url
    assert headers == {"Authorization": f"Client-ID {KEY}", "Accept-Version": "v1"}


def test_unsplash_has_no_video_and_does_not_call_the_api() -> None:
    archive, http = unsplash()
    assert archive.search_assets(video_query()) == []
    assert http.calls == []


def test_unsplash_download_is_announced_before_the_file(tmp_path: Path) -> None:
    archive, http = unsplash()
    [candidate] = archive.search_assets(photo_query())
    archive.download_asset(candidate.asset, tmp_path / "a.jpg")
    (track_url, track_headers), (file_url, file_headers) = http.calls[-2:]
    assert track_url == "https://api.unsplash.com/photos/eOLpJytrbsQ/download"
    assert track_headers["Authorization"] == f"Client-ID {KEY}"
    assert file_url == candidate.asset.original_url and file_headers == {}


def test_unsplash_failed_announcement_blocks_the_download(tmp_path: Path) -> None:
    archive, http = unsplash()
    [candidate] = archive.search_assets(photo_query())
    http.routes["/download"] = TransportError(401, "OAuth error")
    with pytest.raises(ProviderError):
        archive.download_asset(candidate.asset, tmp_path / "a.jpg")
    assert not (tmp_path / "a.jpg").exists()


def test_unsplash_cache_never_holds_the_key(tmp_path: Path) -> None:
    archive, _ = unsplash(tmp_path)
    archive.search_assets(photo_query())
    files = [p for p in (tmp_path / "unsplash").rglob("*") if p.is_file()]
    assert files and all(KEY not in p.read_text(errors="ignore") for p in files)


# --- Transporte ---------------------------------------------------------------------------------


class _Response:
    headers = {"X-Ratelimit-Remaining": "7"}

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        data, self._data = getattr(self, "_data", b'{"ok": true}'), b""
        return data


def test_transport_identifies_itself_and_lowercases_headers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: list[dict[str, str]] = []

    def urlopen(request: Any, timeout: float) -> _Response:
        seen.append(dict(request.header_items()))
        return _Response()

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    response = get_json("https://api.example.org/x", {"Authorization": KEY}, 5)
    assert response.data == {"ok": True} and response.headers == {"x-ratelimit-remaining": "7"}
    download("https://files.example.org/a.mp4", tmp_path / "a.mp4", {}, 5)
    assert all(h["User-agent"] == USER_AGENT for h in seen)  # urllib guarda o nome capitalizado assim
    assert seen[0]["Authorization"] == KEY and "Authorization" not in seen[1]
    assert (tmp_path / "a.mp4").is_file() and not (tmp_path / "a.mp4.part").exists()


@pytest.mark.parametrize(
    ("fixture", "media"),
    [("recorded-videos-pills-blister-pack.json", "video"), ("recorded-photos-cement-bags.json", "photo")],
)
def test_pexels_reads_recorded_real_responses(fixture: str, media: str) -> None:
    routes = {"/videos/search" if media == "video" else "/v1/search": recorded("pexels", fixture)}
    archive, _ = pexels(**routes)
    need = VisualNeed.CONTEXTUAL_STOCK
    query = AssetQuery(text="x", visual_need=need, limit=4, media=media, min_duration_s=4)
    candidates = archive.search_assets(query)
    assert candidates  # o formato real bate com o que o adapter espera
    for c in candidates:
        assert (c.width or 0) > (c.height or 0) and (c.width or 0) >= 1920 and (c.height or 0) >= 1080
        assert c.asset.page_url and c.asset.page_url.startswith("https://www.pexels.com/")
        assert c.asset.author and c.asset.attribution_text.endswith(" via Pexels")
        assert media == "photo" or (c.duration_s or 0) >= 4
