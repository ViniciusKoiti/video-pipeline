from __future__ import annotations

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class ChartPoint(Model):
    label: NonEmpty
    value: float
