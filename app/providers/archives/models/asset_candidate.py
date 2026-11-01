from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.pipeline.models.asset import Asset


@dataclass(frozen=True)
class AssetCandidate:
    asset: Asset  # sempre pending ou needs_review: aprovar é decisão humana (§2.5)
    thumbnail_url: str | None = None
    thumbnail_path: Path | None = None  # miniatura no cache (data/cache/archives/), para a folha de contato
    width: int | None = None  # do arquivo em asset.original_url
    height: int | None = None
    duration_s: float | None = None  # só vídeo
