from __future__ import annotations

from pydantic import Field

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class Generation(Model):
    prompt: NonEmpty
    model: NonEmpty
    seed: int
    steps: int = Field(gt=0)
