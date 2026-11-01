from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Citation:
    scene_id: str
    anchor: str
    asset_id: str
    ms: float
