from __future__ import annotations

from typing import Annotated

from pydantic import Field

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class Person(Model):
    id: Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]
    name: NonEmpty
    role: str = ""
    parent_ids: list[str] = []
