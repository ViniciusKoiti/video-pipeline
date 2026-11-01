from __future__ import annotations

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class CompareSide(Model):
    value: NonEmpty  # como aparece na tela, como no `number`: "69 mil", "R$ 47,6 bi"
    label: NonEmpty
