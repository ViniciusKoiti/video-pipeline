from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VoiceTempo(BaseModel):
    """A velocidade da fala de um episódio (`voice/ritmo.json`): o fator do `atempo` na cópia nivelada."""

    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)

    tempo: float = Field(default=1.0, ge=0.5, le=2.0)
    nota: str = ""
