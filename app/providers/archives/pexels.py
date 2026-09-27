"""Adapter Pexels (§8): fotos e vídeos de ilustração pela API v1, sempre como candidatos em revisão.

Termos em `data/benchmarks/termos-bancos-de-imagem.md`: chave no header `Authorization`, 200 requisições por
hora e 20 mil por mês (headers `X-Ratelimit-*` só em respostas 2xx), crédito "<autor> via Pexels". A chave
só vai para api.pexels.com; o arquivo escolhido é baixado sem ela.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from app.pipeline.schemas import Asset, Provider, Status
from app.providers.archives.base import AssetCandidate, AssetQuery
from app.providers.archives.stock import ArchiveCache, normalize_query, provider_error, utc_now
from app.providers.base import ProviderInfo
from app.providers.errors import ProviderError
from app.providers.http import FileGet, JsonGet, TransportError, download, get_json

API = "https://api.pexels.com/v1"
LICENSE_URL = "https://www.pexels.com/license/"
PER_PAGE = 15  # por busca; os filtros de resolução e duração descartam parte


class PexelsArchive:
    def __init__(
        self,
        api_key: str,
        *,
        cache_dir: Path | None = None,
        min_width: int = 1920,
        min_height: int = 1080,
        timeout_s: float = 30,
        download_timeout_s: float = 300,
        get: JsonGet = get_json,
        get_file: FileGet = download,
        now: Callable[[], datetime] = utc_now,
    ) -> None:
        self.info = ProviderInfo(Provider.PEXELS.value, remote=True)
        self._headers = {"Authorization": api_key}
        self._cache = ArchiveCache(cache_dir, self.info.name, now=now) if cache_dir else None
        self._min_width, self._min_height = min_width, min_height
        self._timeout_s, self._download_timeout_s = timeout_s, download_timeout_s
        self._get, self._get_file, self._now = get, get_file, now

    def search_assets(self, query: AssetQuery) -> list[AssetCandidate]:
        video = query.media == "video"
        params = {"query": normalize_query(query.text), "orientation": "landscape", "per_page": PER_PAGE}
        data = self._search("/videos/search" if video else "/search", params)
        parse = self._video if video else self._photo
        candidates: list[AssetCandidate] = []
        for item in data.get("videos" if video else "photos", []):
            candidate = parse(item, query)
            if candidate is not None and all(c.asset.id != candidate.asset.id for c in candidates):
                candidates.append(candidate)
            if len(candidates) == query.limit:
                break
        return candidates

    def download_asset(self, asset: Asset, dest: Path) -> Path:
        if asset.original_url is None:
            raise ProviderError(self.info.name, f"{asset.id} sem original_url")
        try:
            return self._get_file(asset.original_url, dest, {}, self._download_timeout_s)
        except TransportError as error:
            raise provider_error(self.info.name, error) from None

    def _search(self, path: str, params: Mapping[str, Any]) -> dict[str, Any]:
        def fetch() -> Any:
            return self._get(f"{API}{path}?{urlencode(params)}", self._headers, self._timeout_s)

        try:
            if self._cache is None:
                return fetch().data
            return self._cache.search({"endpoint": path, **params}, fetch)
        except TransportError as error:
            raise provider_error(self.info.name, error) from None

    def _video(self, item: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        duration = float(item.get("duration") or 0)
        if query.min_duration_s is not None and duration < query.min_duration_s:
            return None
        files = [  # hls vem sem largura e altura e cai aqui, junto com o que fica abaixo de 1080p
            f
            for f in item.get("video_files", [])
            if f.get("file_type") == "video/mp4" and self._fits(f.get("width"), f.get("height"))
        ]
        if not files:
            return None
        chosen = min(files, key=lambda f: (f["height"], f["width"]))  # o menor que ainda chega a 1080p
        author = item["user"]["name"]
        asset = self._asset(f"pexels-video-{item['id']}", item, chosen["link"], author)
        return self._candidate(asset, item.get("image"), chosen["width"], chosen["height"], duration)

    def _photo(self, item: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        width, height = int(item.get("width") or 0), int(item.get("height") or 0)
        if not self._fits(width, height):
            return None
        asset = self._asset(f"pexels-photo-{item['id']}", item, item["src"]["original"], item["photographer"])
        return self._candidate(asset, item["src"].get("medium"), width, height, None)

    def _fits(self, width: int | None, height: int | None) -> bool:
        """Horizontal e pelo menos 1920×1080: o vídeo é 16:9 (ADR 007)."""
        width, height = width or 0, height or 0
        return width > height and width >= self._min_width and height >= self._min_height

    def _asset(self, asset_id: str, item: Mapping[str, Any], file_url: str, author: str) -> Asset:
        return Asset(
            id=asset_id,
            provider=Provider.PEXELS,
            provider_id=str(item["id"]),
            original_url=file_url,
            page_url=item["url"],
            author=author,
            license_id="Pexels",
            license_url=LICENSE_URL,
            attribution_text=f"{author} via Pexels",
            retrieved_at=self._now(),
            review_status=Status.NEEDS_REVIEW,  # conferência de pessoas, marcas e texto é humana (ADR 007)
        )

    def _candidate(
        self, asset: Asset, thumb_url: str | None, width: int, height: int, duration: float | None
    ) -> AssetCandidate:
        thumb_path = None
        if self._cache is not None and thumb_url:
            try:
                thumb_path = self._cache.thumbnail(
                    asset.id, thumb_url, lambda url, dest: self._get_file(url, dest, {}, self._timeout_s)
                )
            except TransportError as error:
                raise provider_error(self.info.name, error) from None
        return AssetCandidate(asset, thumb_url, thumb_path, width, height, duration)
