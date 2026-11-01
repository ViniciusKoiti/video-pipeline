from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import MAX_MUSIC_GAIN_DB, AssetId, RelPath
from app.pipeline.models.model import Model


class EpisodeMusic(Model):
    """Trecho da trilha com o tempo resolvido sobre os WAVs reais (ADR 030), relativo ao início do vídeo."""

    asset_id: AssetId
    media: RelPath  # arquivo da faixa na pasta do episódio
    role: Literal["bed", "sting"]
    start_ms: int = Field(ge=0)
    end_ms: int = Field(gt=0)
    track_offset_ms: int = Field(default=0, ge=0)
    gain_db: float = Field(le=MAX_MUSIC_GAIN_DB)
    fade_in_ms: int = Field(default=0, ge=0)
    fade_out_ms: int = Field(default=0, ge=0)
    loop: bool = False  # a faixa recomeça quando acaba

    @model_validator(mode="after")
    def _inside(self) -> Self:
        if self.end_ms <= self.start_ms:
            raise ValueError(f"trilha {self.asset_id}: termina antes de começar")
        if self.fade_in_ms + self.fade_out_ms > self.end_ms - self.start_ms:
            raise ValueError(f"trilha {self.asset_id}: fades maiores que o trecho")
        return self
