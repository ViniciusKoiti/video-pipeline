from __future__ import annotations

from pydantic import Field

from app.pipeline.models._schemas_types import FactId, NonEmpty
from app.pipeline.models.evidence import Evidence
from app.pipeline.models.fact_kind import FactKind
from app.pipeline.models.model import Model


class Fact(Model):
    id: FactId
    text: NonEmpty  # o fato com palavras próprias, no idioma do episódio
    kind: FactKind
    when: str | None = None  # como a fonte dá: "1918", "ago. 1925"
    people: list[str] = []
    why_it_matters: NonEmpty  # por que o público se importaria
    evidence: list[Evidence] = Field(min_length=1)

    @property
    def source_ids(self) -> list[str]:
        return sorted({e.excerpt_id.split("#")[0] for e in self.evidence})
