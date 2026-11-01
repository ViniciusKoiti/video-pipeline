from __future__ import annotations

from pydantic import ConfigDict, Field

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class _FromTo(Model):
    """`from` é palavra reservada no Python: o campo se chama `from_` e o JSON continua com "from"."""

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, serialize_by_alias=True, validate_by_name=True
    )

    from_: NonEmpty = Field(alias="from")
    to: NonEmpty
