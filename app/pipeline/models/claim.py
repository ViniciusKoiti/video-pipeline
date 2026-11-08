from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import ExcerptId, NonEmpty, SourceId
from app.pipeline.models.model import Model


class Claim(Model):
    text: NonEmpty
    source_ids: list[SourceId] = Field(min_length=1)  # §2.2: toda claim tem fonte
    excerpt_ids: list[ExcerptId] = []  # opcional até a ADR 002 (etapa 26)

    @model_validator(mode="after")
    def _excerpts_belong_to_sources(self) -> Self:
        foreign = [e for e in self.excerpt_ids if e.split("#")[0] not in self.source_ids]
        if foreign:
            raise ValueError(f"trechos de fontes fora de source_ids: {', '.join(foreign)}")
        return self
