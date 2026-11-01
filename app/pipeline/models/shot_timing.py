from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models._schemas_value_shot import Shot


@dataclass(frozen=True)
class ShotTiming:
    scene_id: str
    shot: Shot
    start_ms: float  # desde o começo do vídeo
    ms: float
