"""Adapter Pixabay (§8): vídeos e fotos de ilustração pela API, sempre como candidatos em revisão.

Termos em `data/benchmarks/termos-bancos-de-imagem.md`: chave no parâmetro `key` (a URL nunca vai para log
nem para o cache), 100 requisições por 60 s, respostas em cache por 24 h (o cache daqui não expira),
arquivo baixado em vez de hotlink, crédito "<autor> via Pixabay". Sem acesso completo aprovado, a maior
foto tem 1280 px no lado maior e não chega a 1920: na prática o Pixabay serve para vídeo.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlencode

from app.pipeline.schemas import Provider
from app.providers.archives.base import AssetCandidate, AssetQuery
from app.providers.archives.stock import StockArchive, normalize_query

API = "https://pixabay.com/api/"
PER_PAGE = 20
MAX_QUERY_CHARS = 100  # limite da API para `q`


class PixabayArchive(StockArchive):
    provider = Provider.PIXABAY
    license_id = "Pixabay"
    license_url = "https://pixabay.com/service/license-summary/"

    def __init__(self, api_key: str, **options: Any) -> None:
        super().__init__(**options)
        self._key = api_key

    def _results(self, query: AssetQuery) -> list[Mapping[str, Any]]:
        video = query.media == "video"
        portrait = query.orientation == "portrait"
        min_width, min_height = self._min_width, self._min_height
        if portrait:  # o mínimo é 1920×1080 deitado; em pé, 1080×1920
            min_width, min_height = min_height, min_width
        params: dict[str, Any] = {
            "q": normalize_query(query.text)[:MAX_QUERY_CHARS],
            "min_width": min_width,
            "min_height": min_height,
            "safesearch": "true",
            "per_page": PER_PAGE,
        }
        # o vídeo não tem filtro de orientação na API: o corte em pé sai do `_fits` de cada arquivo
        params |= {"video_type": "film"} if video else {
            "image_type": "photo",
            "orientation": "vertical" if portrait else "horizontal",
        }
        endpoint = f"{API}videos/" if video else API
        url = f"{endpoint}?{urlencode({'key': self._key, **params})}"
        data = self._fetch(url, {}, {"endpoint": "videos" if video else "images", **params})
        return data.get("hits", [])

    def _parse(self, item: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        return self._video(item, query) if query.media == "video" else self._photo(item, query)

    def _video(self, hit: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        # A documentação não diz a unidade de `duration`; o exemplo (12) é de segundos. Conferir no passo 5.
        duration = float(hit.get("duration") or 0)
        renditions = [  # large pode vir com URL vazia; tiny e small ficam abaixo de 1080p
            r
            for r in (hit.get("videos") or {}).values()
            if r.get("url") and self._fits(r.get("width"), r.get("height"), query.orientation)
        ]
        if not renditions or not self._long_enough(duration, query):
            return None
        chosen = min(renditions, key=lambda r: (r["height"], r["width"]))  # o menor que ainda chega a 1080p
        return self._candidate(
            hit["id"],
            media="video",
            file_url=chosen["url"],
            page_url=hit["pageURL"],
            author=hit["user"],
            thumb_url=chosen.get("thumbnail"),
            width=chosen["width"],
            height=chosen["height"],
            duration=duration,
        )

    def _photo(self, hit: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        # fullHDURL (até 1920 px) só com acesso completo aprovado; sem ele, largeImageURL (até 1280 px).
        url, max_side = (hit["fullHDURL"], 1920) if hit.get("fullHDURL") else (hit.get("largeImageURL"), 1280)
        width, height = _scaled(hit.get("imageWidth"), hit.get("imageHeight"), max_side)
        if not url or not self._fits(width, height, query.orientation):
            return None
        return self._candidate(
            hit["id"],
            media="photo",
            file_url=url,
            page_url=hit["pageURL"],
            author=hit["user"],
            thumb_url=hit.get("webformatURL"),
            width=width,
            height=height,
        )


def _scaled(width: int | None, height: int | None, max_side: int) -> tuple[int, int]:
    """Tamanho do arquivo servido: o original reduzido até `max_side` no lado maior."""
    width, height = int(width or 0), int(height or 0)
    scale = min(1.0, max_side / max(width, height, 1))
    return round(width * scale), round(height * scale)
