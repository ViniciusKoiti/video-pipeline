from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import _unique
from app.pipeline.models.model import Model
from app.pipeline.models.narration_line import NarrationLine


class Narration(Model):
    language: str
    lines: list[NarrationLine] = Field(min_length=1)

    @model_validator(mode="after")
    def _one_line_per_scene(self) -> Self:
        _unique([line.scene for line in self.lines if line.scene], "cenas da narração")
        return self
