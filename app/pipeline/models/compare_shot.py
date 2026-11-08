from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import screen_parts
from app.pipeline.models.compare_side import CompareSide


class CompareShot(_FactualShot):
    """Dois valores lado a lado; a tela não calcula razão nem variação (ADR 011, decisão 7). Um valor
    calculado pelo roteiro entra só como conta dita inteira, com insumos e regra em fichas (ADR 020)."""

    kind: Literal["compare"] = "compare"
    left: CompareSide
    right: CompareSide
    mode: Literal["side", "before_after", "scale"] = "side"
    emphasis: Literal["left", "right"] | None = None  # só o peso da fonte; o outro lado não apaga

    @model_validator(mode="after")
    def _scale_needs_same_unit(self) -> Self:
        if self.mode != "scale":
            return self
        # A unidade (prefixo e sufixo) não depende do idioma, então aqui o número não é lido: "US$ 1,234,567"
        # é número em inglês, e seria recusado se lido como pt-BR.
        left, right = screen_parts(self.left.value), screen_parts(self.right.value)
        if left is None or right is None:
            raise ValueError("comparação em escala precisa de dois números")
        if (left[0], left[2]) != (right[0], right[2]):
            raise ValueError(
                f"comparação em escala com unidades diferentes: {self.left.value!r} e {self.right.value!r}"
            )
        return self
