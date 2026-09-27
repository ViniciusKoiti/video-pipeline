"""Porta de busca em acervos e bancos de imagem. A ordem da cascata vem de config/providers.toml (§8)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from app.pipeline.schemas import Asset, VisualNeed
from app.providers.base import ProviderInfo

Media = Literal["photo", "video"]


@dataclass(frozen=True)
class AssetQuery:
    text: str
    visual_need: VisualNeed
    limit: int = 2  # MAX_CANDIDATES_PER_SCENE
    media: Media = "photo"  # "video" = B-roll em movimento
    min_duration_s: float | None = None  # vídeo: pelo menos a duração do plano


@dataclass(frozen=True)
class AssetCandidate:
    asset: Asset  # sempre pending ou needs_review: aprovar é decisão humana (§2.5)
    thumbnail_url: str | None = None
    thumbnail_path: Path | None = None  # miniatura no cache (data/cache/archives/), para a folha de contato
    width: int | None = None  # do arquivo em asset.original_url
    height: int | None = None
    duration_s: float | None = None  # só vídeo


class ArchiveProvider(Protocol):
    info: ProviderInfo

    def search_assets(self, query: AssetQuery) -> list[AssetCandidate]: ...

    def download_asset(self, asset: Asset, dest: Path) -> Path: ...
