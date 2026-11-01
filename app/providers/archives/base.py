"""Porta de busca em acervos e bancos de imagem. A ordem da cascata vem de config/providers.toml (§8)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.pipeline.schemas import Asset
from app.providers.archives.models._base_types import Media as Media
from app.providers.archives.models.asset_candidate import AssetCandidate as AssetCandidate
from app.providers.archives.models.asset_query import AssetQuery as AssetQuery
from app.providers.base import ProviderInfo


class ArchiveProvider(Protocol):
    info: ProviderInfo

    def search_assets(self, query: AssetQuery) -> list[AssetCandidate]: ...

    def download_asset(self, asset: Asset, dest: Path) -> Path: ...
