"""Porta de busca em acervos e bancos de imagem. A ordem da cascata vem de config/providers.toml (§8)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.pipeline.schemas import Asset, VisualNeed
from app.providers.base import ProviderInfo


@dataclass(frozen=True)
class AssetQuery:
    text: str
    visual_need: VisualNeed
    limit: int = 2  # MAX_CANDIDATES_PER_SCENE


@dataclass(frozen=True)
class AssetCandidate:
    asset: Asset  # sempre pending ou needs_review: aprovar é decisão humana (§2.5)
    thumbnail_url: str | None = None


class ArchiveProvider(Protocol):
    info: ProviderInfo

    def search_assets(self, query: AssetQuery) -> list[AssetCandidate]: ...

    def download_asset(self, asset: Asset, dest: Path) -> Path: ...
