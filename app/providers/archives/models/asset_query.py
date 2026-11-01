from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models._schemas_types import Orientation
from app.pipeline.models.visual_need import VisualNeed
from app.providers.archives.models._base_types import Media


@dataclass(frozen=True)
class AssetQuery:
    text: str
    visual_need: VisualNeed
    limit: int = 2  # MAX_CANDIDATES_PER_SCENE
    media: Media = "photo"  # "video" = B-roll em movimento
    min_duration_s: float | None = None  # vídeo: pelo menos a duração do plano
    orientation: Orientation = "landscape"  # "portrait": arquivo em pé para o vídeo 9:16 (ADR 014)
