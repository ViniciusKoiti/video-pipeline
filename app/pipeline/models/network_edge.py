from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.pipeline.models._schemas_from_to import _FromTo
from app.pipeline.models.claim import Claim


class NetworkEdge(_FromTo):
    label: str = ""  # a relação ("controla", "empresta a")
    value: str = ""  # valor na seta, como aparece na tela
    style: Literal["solid", "dashed"] = "solid"  # tracejada: relação indireta
    flow: bool = False  # dinheiro correndo de `from` para `to`
    claims: list[Claim] = Field(min_length=1)  # cada relação é uma afirmação (§2.2)
