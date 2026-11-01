from __future__ import annotations

from app.pipeline.models._molde_molde import _Molde


class Traco(_Molde):
    com: int
    n: int
    pct: int
    forca: str  # padrao | indicio
    unidade: str = "videos"
