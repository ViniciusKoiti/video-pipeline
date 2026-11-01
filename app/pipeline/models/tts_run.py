from __future__ import annotations

from pydantic import BaseModel


class TtsRun(BaseModel):
    provider: str
    voice: str = ""
    run: int
    ok: bool
    error: str = ""
    wall_s: float
    audio_s: float = 0.0
    rtf: float | None = None  # segundos de síntese por segundo de áudio
    seconds_per_audio_minute: float | None = None
