from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import _later_steps_anchored
from app.pipeline.models.calculation_result import CalculationResult
from app.pipeline.models.calculation_term import CalculationTerm


class CalculationShot(_FactualShot):
    """Conta animada (`Equation` do kit). A tela não calcula: termos e resultado vêm escritos, a narração diz
    a conta inteira e o `vp check` a refaz (ADR 020 e 028). Só em vídeo que explica."""

    kind: Literal["calculation"] = "calculation"
    terms: list[CalculationTerm] = Field(min_length=2)
    result: CalculationResult

    @model_validator(mode="after")
    def _operators_and_anchors(self) -> Self:
        if self.terms[0].op is not None:
            raise ValueError("o primeiro termo da conta não tem operador")
        missing = [i + 1 for i, term in enumerate(self.terms) if i > 0 and term.op is None]
        if missing:
            raise ValueError(f"termo {', '.join(map(str, missing))} da conta sem operador (op)")
        _later_steps_anchored(list(self.terms), "termo")
        return self
