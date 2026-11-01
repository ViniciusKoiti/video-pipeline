from __future__ import annotations

from typing import TYPE_CHECKING

from app.pipeline.models.calculation_shot import CalculationShot
from app.pipeline.models.network_shot import NetworkShot
from app.pipeline.models.receipt_shot import ReceiptShot

if TYPE_CHECKING:
    from app.pipeline.models._schemas_value_shot import Shot


def step_anchors(shot: Shot) -> list[str | None]:
    """Âncora de cada parte que entra no ritmo da narração: passos da rede, termos e resultado da conta,
    linhas e total da nota. Sem âncora (só a primeira), a parte entra com o plano."""
    if isinstance(shot, NetworkShot):
        return [step.anchor for step in shot.steps]
    if isinstance(shot, CalculationShot):
        return [term.anchor for term in shot.terms] + [shot.result.anchor]
    if isinstance(shot, ReceiptShot):
        return [item.anchor for item in shot.items] + ([shot.total.anchor] if shot.total else [])
    return []
