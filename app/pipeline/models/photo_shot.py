from __future__ import annotations

from typing import Literal

from app.pipeline.models._schemas_shot import _Shot
from app.pipeline.models._schemas_types import AssetId, Motion, NonEmpty
from app.pipeline.models.crop import Crop
from app.pipeline.models.visual_need import VisualNeed


class PhotoShot(_Shot):
    kind: Literal["photo"] = "photo"
    visual_need: VisualNeed
    search_query: NonEmpty
    asset_id: AssetId | None = None
    crop: Crop | None = None
    motion: Motion = "push_in"
