from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.constants.checagem_local_constants import ChecagemLocalConstants
from app.pipeline.models._checagem_local_types import Rotulo


@dataclass(frozen=True)
class Case:
    id: str
    kind: str
    claim: str
    excerpt_ids: tuple[str, ...]
    excerpt: str

    @property
    def expected(self) -> Rotulo:
        return ChecagemLocalConstants.EXPECTED[self.kind]
