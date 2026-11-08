from __future__ import annotations

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class CalculationResult(Model):
    text: NonEmpty  # escrito pelo roteirista, arredondado como se fala; o `vp check` refaz a conta
    label: str = ""
    anchor: NonEmpty  # o resultado entra quando é dito
