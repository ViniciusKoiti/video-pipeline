from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import _later_steps_anchored
from app.pipeline.models.receipt_item import ReceiptItem
from app.pipeline.models.receipt_total import ReceiptTotal


class ReceiptShot(_FactualShot):
    """Nota ou orçamento (`Receipt` do kit): uma linha por item, no ritmo da narração, e o total opcional.
    Serve ao dinheiro, um valor por linha na mesma moeda (ADR 028, decisão 3)."""

    kind: Literal["receipt"] = "receipt"
    title: str = ""
    items: list[ReceiptItem] = Field(min_length=2)
    total: ReceiptTotal | None = None

    @model_validator(mode="after")
    def _anchors(self) -> Self:
        _later_steps_anchored(list(self.items), "linha")
        return self
