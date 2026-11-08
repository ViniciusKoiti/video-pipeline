from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class FfmpegSettings(_Model):
    crf: int = Field(default=20, ge=0, le=51)
    preset_final: str = "medium"
    preset_preview: str = "veryfast"
    zoom: float = Field(default=0.06, ge=0, le=0.3)
    fade_s: float = Field(default=0.3, ge=0)
    burn_captions_preview: bool = True
    burn_captions_final: bool = False  # captions.srt sobe separado no YouTube
