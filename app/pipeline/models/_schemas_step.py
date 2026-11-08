from __future__ import annotations

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class _Step(Model):
    """Parte de um plano que entra quando a narração a diz: na `anchor`, em ordem, dentro do trecho do plano.
    Só a primeira pode ficar sem `anchor`: entra com o plano."""

    anchor: NonEmpty | None = None
