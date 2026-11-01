from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import _WHEN_RE, NonEmpty
from app.pipeline.models.chart_point import ChartPoint


class ChartShot(_FactualShot):
    kind: Literal["chart"] = "chart"
    title: NonEmpty
    unit: str = ""
    points: list[ChartPoint] = Field(min_length=2)
    type: Literal["bar", "bar_horizontal", "line", "share"] = "bar"  # ADR 011
    highlight: str | None = None  # rótulo do ponto em destaque; sem ele, nenhum destaque
    y_from_zero: bool = True  # só `line`: eixo a partir do zero, para não exagerar variação pequena
    rest: str | None = None  # só `share`: rótulo da fatia do que sobra (ex.: "outros")

    @model_validator(mode="after")
    def _consistent_type(self) -> Self:
        labels = [p.label for p in self.points]
        if self.highlight is not None and self.highlight not in labels:
            raise ValueError(f"destaque {self.highlight!r} não é um dos rótulos do gráfico")
        if self.type == "line" and not all(_WHEN_RE.match(label) for label in labels):
            raise ValueError("gráfico de linha: os rótulos precisam ser anos (1927) ou datas ISO")
        if self.type == "share" and any(p.value < 0 for p in self.points):
            raise ValueError("gráfico de participação sem valor negativo")
        if self.rest is not None and self.type != "share":
            raise ValueError("rest só vale no gráfico de participação (type share)")
        return self
