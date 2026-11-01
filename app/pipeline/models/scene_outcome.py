from __future__ import annotations

from dataclasses import dataclass
from typing import Generic

from app.pipeline.models._failures_types import R
from app.pipeline.models.status import Status


@dataclass(frozen=True)
class SceneOutcome(Generic[R]):
    scene_id: str
    status: Status  # COMPLETED ou NEEDS_REVIEW
    value: R | None = None
    reason: str = ""  # ProviderError.reason, para registrar em review.json
    detail: str = ""
