from __future__ import annotations

from typing import Literal

from app.pipeline.models._numbers_brief import _Brief


class FormatMeasure(_Brief):
    alto: float  # mediana do terço de mais views
    baixo: float  # mediana do terço de menos views
    rho: float | None = None  # Spearman com log das views
    n: int
    forca: Literal["pattern", "hint"]

    def bottom_side(self, value: float) -> bool:
        """O valor do roteiro está mais perto do terço de baixo que do de cima."""
        return abs(value - self.baixo) < abs(value - self.alto)
