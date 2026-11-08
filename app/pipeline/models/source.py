from __future__ import annotations

from typing import Self

from pydantic import AwareDatetime, model_validator

from app.pipeline.models._schemas_types import HttpUrl, NonEmpty, RelPath, SourceId
from app.pipeline.models.model import Model
from app.pipeline.models.source_kind import SourceKind


class Source(Model):
    id: SourceId
    title: NonEmpty
    url: HttpUrl | None = None  # obrigatória, salvo na fonte declarada (`kind: declared`)
    kind: SourceKind
    retrieved_at: AwareDatetime
    local_path: RelPath  # texto extraído; um parágrafo = um trecho numerado (ADR 009)
    notes: str = ""
    interested: bool = False  # fonte interessada (a própria empresa ou família): nenhum fato só com ela
    authors: list[str] = []  # fontes que compartilham autor contam como uma só para independência (ADR 009)

    @model_validator(mode="after")
    def _url_unless_declared(self) -> Self:
        if self.url is None and self.kind is not SourceKind.DECLARED:
            raise ValueError(f"{self.id}: fonte {self.kind.value} sem url; só `declared` dispensa a URL")
        return self
