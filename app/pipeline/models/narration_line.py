from __future__ import annotations

from typing import Annotated

from pydantic import StringConstraints

from app.pipeline.models._schemas_types import Delivery, NonEmpty
from app.pipeline.models.model import Model

SpokenText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class NarrationLine(Model):
    scene: NonEmpty | None = None  # id da cena do vídeo; None = fala de um plano fora do JSON
    text: SpokenText  # o que a voz lê, sem as pontas em branco
    delivery: Delivery | None = None  # hook | turn | calm | invite (ADR 022); sem o campo, neutra
