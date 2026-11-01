from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models._checagem_local_types import EXPECTED, Rotulo


@dataclass(frozen=True)
class Case:
    id: str
    kind: str
    claim: str
    excerpt_ids: tuple[str, ...]
    excerpt: str

    @property
    def expected(self) -> Rotulo:
        return EXPECTED[self.kind]
