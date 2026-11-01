from __future__ import annotations

from app.pipeline.models._molde_molde import _Molde


class Medida(_Molde):
    mediana: float
    n: int
    q1: float | None = None
    q3: float | None = None
    origem: str = ""
