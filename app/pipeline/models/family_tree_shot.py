from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import _unique
from app.pipeline.models.person import Person


class FamilyTreeShot(_FactualShot):
    kind: Literal["family_tree"] = "family_tree"
    people: list[Person] = Field(min_length=2)

    @model_validator(mode="after")
    def _parents_exist(self) -> Self:
        ids = {p.id for p in self.people}
        _unique([p.id for p in self.people], "pessoas")
        missing = sorted({pid for p in self.people for pid in p.parent_ids} - ids)
        if missing:
            raise ValueError(f"pais inexistentes na árvore: {', '.join(missing)}")
        return self
