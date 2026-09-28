"""Adapter Pexels (§8): fotos e vídeos de ilustração pela API v1, sempre como candidatos em revisão.

Termos em `data/benchmarks/termos-bancos-de-imagem.md`: chave no header `Authorization`, 200 requisições por
hora e 20 mil por mês (headers `X-Ratelimit-*` só em respostas 2xx), crédito "<autor> via Pexels". A chave
só vai para api.pexels.com; o arquivo escolhido é baixado sem ela.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlencode

from app.pipeline.schemas import Provider
from app.providers.archives.base import AssetCandidate, AssetQuery
from app.providers.archives.stock import StockArchive, normalize_query

API = "https://api.pexels.com/v1"
PER_PAGE = 15  # por busca; os filtros de resolução e duração descartam parte


class PexelsArchive(StockArchive):
    provider = Provider.PEXELS
    license_id = "Pexels"
    license_url = "https://www.pexels.com/license/"

    def __init__(self, api_key: str, **options: Any) -> None:
        super().__init__(**options)
        self._headers = {"Authorization": api_key}

    def _results(self, query: AssetQuery) -> list[Mapping[str, Any]]:
        video = query.media == "video"
        path = "/videos/search" if video else "/search"
        params = {"query": normalize_query(query.text), "orientation": "landscape", "per_page": PER_PAGE}
        data = self._fetch(f"{API}{path}?{urlencode(params)}", self._headers, {"endpoint": path, **params})
        return data.get("videos" if video else "photos", [])

    def _parse(self, item: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        return self._video(item, query) if query.media == "video" else self._photo(item)

    def _video(self, item: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        duration = float(item.get("duration") or 0)
        files = [  # hls vem sem largura e altura e cai aqui, junto com o que fica abaixo de 1080p
            f
            for f in item.get("video_files", [])
            if f.get("file_type") == "video/mp4" and self._fits(f.get("width"), f.get("height"))
        ]
        if not files or not self._long_enough(duration, query):
            return None
        chosen = min(files, key=lambda f: (f["height"], f["width"]))  # o menor que ainda chega a 1080p
        return self._candidate(
            item["id"],
            media="video",
            file_url=chosen["link"],
            page_url=item["url"],
            author=item["user"]["name"],
            thumb_url=item.get("image"),
            width=chosen["width"],
            height=chosen["height"],
            duration=duration,
        )

    def _photo(self, item: Mapping[str, Any]) -> AssetCandidate | None:
        width, height = int(item.get("width") or 0), int(item.get("height") or 0)
        if not self._fits(width, height):
            return None
        return self._candidate(
            item["id"],
            media="photo",
            file_url=item["src"]["original"],
            page_url=item["url"],
            author=item["photographer"],
            thumb_url=item["src"].get("medium"),
            width=width,
            height=height,
        )
