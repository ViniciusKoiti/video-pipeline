from __future__ import annotations

from pydantic import Field

from app.pipeline.models._checagem_local_types import Rotulo
from app.pipeline.models.model import Model


class Veredito(Model):
    """`confronto` vem antes: o modelo escreve a comparação e só depois decide."""

    confronto: str = Field(min_length=1, pattern=r"\S")
    veredito: Rotulo
