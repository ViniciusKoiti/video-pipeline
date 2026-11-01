from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import Orientation
from app.pipeline.models.model import Model


class VideoSpec(Model):
    width: int = Field(default=1920, gt=0)
    height: int = Field(default=1080, gt=0)
    fps: int = Field(default=30, gt=0)
    audio_sample_rate: int = Field(default=48_000, gt=0)

    @model_validator(mode="after")
    def _sixteen_by_nine_either_way(self) -> Self:
        if self.width * 9 != self.height * 16 and self.width * 16 != self.height * 9:
            raise ValueError(f"{self.width}x{self.height} não é 16:9 nem 9:16")
        return self

    @property
    def portrait(self) -> bool:
        return self.height > self.width

    @classmethod
    def for_orientation(cls, orientation: Orientation) -> VideoSpec:
        """1920×1080 em paisagem e 1080×1920 em retrato (ADR 014)."""
        return cls(width=1080, height=1920) if orientation == "portrait" else cls()
