from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class Series(Model):
    """A série do vídeo, para o selo do cartão final ("Parte 2 de 3"; ADR 028)."""

    name: NonEmpty
    part: int = Field(ge=1)
    total: int = Field(ge=2)

    @model_validator(mode="after")
    def _part_inside(self) -> Self:
        if self.part > self.total:
            raise ValueError(f"série: parte {self.part} de {self.total}")
        return self
