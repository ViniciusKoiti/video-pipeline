from __future__ import annotations

from pydantic import BaseModel


class RenderRun(BaseModel):
    engine: str
    mode: str  # final-frio | final-cache | preview-frio
    ok: bool
    error: str = ""
    wall_s: float
    video_s: float = 0.0
    width: int = 0
    height: int = 0
    output_mb: float = 0.0
    realtime_factor: float | None = None  # segundos de vídeo por segundo de render (> 1 = mais rápido)
    peak_child_rss_mb: int = 0  # maior processo filho (ffmpeg) medido até aqui
