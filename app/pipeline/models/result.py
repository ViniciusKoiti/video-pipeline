from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models._checagem_local_types import Rotulo
from app.pipeline.models.case import Case


@dataclass(frozen=True)
class Result:
    case: Case
    verdict: Rotulo | None  # None = o modelo não devolveu JSON válido
    confronto: str
    error: str
    seconds: float
