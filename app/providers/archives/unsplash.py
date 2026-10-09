"""Adapter Unsplash (§8): fotos de ilustração pela API, sempre como candidatos em revisão. Não há vídeo.

Termos em `data/benchmarks/termos-bancos-de-imagem.md` e decisão do dono na emenda de bancos de imagem da
ADR 007: chave em `Authorization: Client-ID`, 50 requisições por hora em modo demo; a cada download, aviso
em `GET /photos/:id/download` antes de baixar o arquivo; crédito "Photo by <autor> on Unsplash" com links
para o perfil e para o Unsplash (`utm_source`, `utm_medium=referral`). A foto editada no vídeo é tratada
como obra derivada, dispensada do hotlink pelas diretrizes. A chave só vai para api.unsplash.com.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from app.pipeline.schemas import Asset, Provider
from app.providers.archives.base import AssetCandidate, AssetQuery
from app.providers.archives.stock import StockArchive, normalize_query, provider_error
from app.providers.http import TransportError

API = "https://api.unsplash.com"
PER_PAGE = 20


class UnsplashArchive(StockArchive):
    provider = Provider.UNSPLASH
    license_id = "Unsplash"
    license_url = "https://unsplash.com/license"

    def __init__(self, access_key: str, *, app_name: str = "video_pipeline", **options: Any) -> None:
        super().__init__(**options)
        self._headers = {"Authorization": f"Client-ID {access_key}", "Accept-Version": "v1"}
        self._utm = urlencode({"utm_source": app_name, "utm_medium": "referral"})

    def download_asset(self, asset: Asset, dest: Path) -> Path:
        """Termos da API: avisar cada download no endpoint de rastreio, com a chave, antes de baixar."""
        try:
            self._get(f"{API}/photos/{asset.provider_id}/download", self._headers, self._timeout_s)
        except TransportError as error:
            raise provider_error(self.info.name, error) from None
        return super().download_asset(asset, dest)

    def _results(self, query: AssetQuery) -> list[Mapping[str, Any]]:
        if query.media == "video":
            return []  # a API do Unsplash não tem vídeo
        params = {
            "query": normalize_query(query.text),
            "orientation": query.orientation,
            "content_filter": "high",
            "per_page": PER_PAGE,
        }
        data = self._fetch(f"{API}/search/photos?{urlencode(params)}", self._headers, params)
        return data.get("results", [])

    def _parse(self, item: Mapping[str, Any], query: AssetQuery) -> AssetCandidate | None:
        width, height = int(item.get("width") or 0), int(item.get("height") or 0)
        if not self._fits(width, height, query.orientation):
            return None
        user = item["user"]
        profile = f"{user['links']['html']}?{self._utm}"
        return self._candidate(
            item["id"],
            media="photo",
            file_url=item["urls"]["full"],  # as diretrizes mandam baixar urls.full, com os parâmetros dela
            page_url=item["links"]["html"],
            author=user["name"],
            thumb_url=item["urls"].get("small"),
            width=width,
            height=height,
            credit=f"Photo by {user['name']} on Unsplash ({profile} · https://unsplash.com/?{self._utm})",
        )
