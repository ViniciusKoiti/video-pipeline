from __future__ import annotations

from datetime import date
from typing import Annotated, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import READING_NUMBERS, Count, Percent, _unique
from app.pipeline.models.model import Model
from app.pipeline.models.traffic_source import TrafficSource


class MetricsReading(Model):
    """Uma leitura manual (YouTube Studio ou Instagram). O que não foi lido fica `null`, nunca zero."""

    read_at: date
    views: Count | None = None
    likes: Count | None = None
    shares: Count | None = None
    comments: Count | None = None
    saves: Count | None = None
    impressions: Count | None = None  # só YouTube
    ctr_percent: Percent | None = None  # cliques por impressão, em %
    avg_view_duration_s: Annotated[float, Field(ge=0)] | None = None
    retention_30s_percent: Percent | None = None  # público que passa dos 30 s iniciais
    subscribers_gained: int | None = None  # líquido; pode ser negativo
    traffic_sources: list[TrafficSource] = []
    notes: str = ""

    @model_validator(mode="after")
    def _has_numbers(self) -> Self:
        if all(getattr(self, name) is None for name in READING_NUMBERS) and not self.traffic_sources:
            raise ValueError("leitura sem nenhum número: o que não foi lido fica fora, não zero")
        _unique([source.name for source in self.traffic_sources], "origens de tráfego")
        total = sum(source.percent for source in self.traffic_sources)
        if total > 100.5:
            raise ValueError(f"origens de tráfego somam {total:g}%, acima de 100%")
        return self
