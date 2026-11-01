from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models.model import Model


class Crop(Model):
    """Recorte normalizado (0–1) de uma foto: o detalhe que o plano mostra (um rosto, o nome no casco)."""

    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def _inside_image(self) -> Self:
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("recorte sai da imagem")
        return self
