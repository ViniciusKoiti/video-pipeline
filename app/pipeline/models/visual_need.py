from __future__ import annotations

from enum import StrEnum


class VisualNeed(StrEnum):
    HISTORICAL_EXACT = "historical_exact"
    CONTEXTUAL_STOCK = "contextual_stock"
    MAP_OR_GRAPHIC = "map_or_graphic"
    ILLUSTRATIVE_RECONSTRUCTION = "illustrative_reconstruction"
