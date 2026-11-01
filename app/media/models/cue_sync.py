from __future__ import annotations

from dataclasses import dataclass

from app.media.models._earshot_types import SYNC_TOLERANCE_MS


@dataclass(frozen=True)
class CueSync:
    at_s: float  # o corte que pedimos
    status: str  # OK | near | swell | peak | no hit (como o earshot classifica)
    offset_ms: float | None  # o ataque mais próximo, em ms depois (+) ou antes (−) do corte
    event: str | None  # a etiqueta do earshot para o som ali (palpite dele, não medida)

    @property
    def hit(self) -> bool:
        return self.offset_ms is not None and abs(self.offset_ms) <= SYNC_TOLERANCE_MS
