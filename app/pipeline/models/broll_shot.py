from __future__ import annotations

from typing import Literal

from app.pipeline.models._schemas_shot import _Shot
from app.pipeline.models._schemas_types import AssetId, NonEmpty
from app.pipeline.models.visual_need import VisualNeed


class BrollShot(_Shot):
    kind: Literal["broll"] = "broll"  # vídeo em movimento (banco de imagens ou filme de arquivo)
    visual_need: VisualNeed
    search_query: NonEmpty
    asset_id: AssetId | None = None
