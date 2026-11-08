from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VoicePolish(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)

    highpass_hz: float = Field(default=65.0, ge=20, le=200)
    eq_hz: float = Field(default=3000.0, ge=200, le=10000)
    eq_width_octaves: float = Field(default=1.0, ge=0.1, le=5)
    eq_gain_db: float = Field(default=0.0, ge=-6, le=6)
    deesser_intensity: float = Field(default=0.3, ge=0, le=1)
    deesser_max: float = Field(default=0.98, ge=0, le=1)
    deesser_frequency: float = Field(default=1.0, ge=0, le=1)
