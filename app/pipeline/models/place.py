from __future__ import annotations

from pydantic import Field

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class Place(Model):
    name: NonEmpty
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
