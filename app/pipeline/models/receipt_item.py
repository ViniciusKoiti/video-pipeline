from __future__ import annotations

from app.pipeline.models._schemas_step import _Step
from app.pipeline.models._schemas_types import NonEmpty


class ReceiptItem(_Step):
    label: NonEmpty
    value: NonEmpty  # pronto, como a ficha traz, na mesma moeda das outras linhas
    detail: str = ""  # linha pequena embaixo: "2 latas de 395 g"
