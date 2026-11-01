from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostEstimate:
    units: float
    unit: str  # ex.: "neurons"
    usd: float  # > 0 é recusado enquanto ALLOW_PAID_API=false
