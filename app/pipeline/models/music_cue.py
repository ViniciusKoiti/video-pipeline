from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import AssetId, MusicLevel, MusicRole, NonEmpty
from app.pipeline.models.model import Model
from app.pipeline.models.music_anchor import MusicAnchor


class MusicCue(Model):
    role: MusicRole
    track: AssetId | None = None  # o silêncio não tem faixa
    start: MusicAnchor
    end: MusicAnchor
    level: MusicLevel = "low"
    fade_in_ms: int = Field(default=1500, ge=0)
    fade_out_ms: int = Field(default=2500, ge=0)
    track_offset_ms: int = Field(default=0, ge=0)  # de onde a faixa começa a tocar
    why: NonEmpty  # o motivo: a entrega da cena, a virada, a frase que decide

    @model_validator(mode="after")
    def _track_unless_silence(self) -> Self:
        if (self.role == "silence") != (self.track is None):
            raise ValueError("o silêncio não tem faixa; fundo e transição têm")
        return self
