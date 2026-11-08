from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models._schemas_types import (
    HttpUrl,
    NonEmpty,
    Platform,
    PublicationFormat,
    Slug,
    Window,
)
from app.pipeline.models.audience_request import AudienceRequest
from app.pipeline.models.metrics_reading import MetricsReading
from app.pipeline.models.model import Model


class PublicationMetrics(Model):
    """Uma publicação medida à mão aos 7 e aos 28 dias (§12). Vive em `metrics.json` na pasta do episódio;
    sem episódio (clipe, story), em `data/publicacoes/metricas/<id>.json`."""

    schema_version: Literal[1] = 1
    id: Slug
    platform: Platform
    channel: NonEmpty
    format: PublicationFormat
    published_at: AwareDatetime
    url: HttpUrl | None = None
    post_id: str | None = None  # id do post no Postiz
    series: str | None = None
    duration_s: Annotated[float, Field(gt=0)] | None = None
    hypothesis: str | None = None  # hipótese de forma (#122): o que se espera ver e em que medida
    readings: dict[Window, MetricsReading] = {}
    requests: list[AudienceRequest] = []

    def due_date(self, window: Window) -> date:
        """Dia em que a janela fecha, no fuso gravado em `published_at`."""
        return (self.published_at + timedelta(days=SchemasConstants.WINDOW_DAYS[window])).date()

    def pending(self, today: date) -> list[Window]:
        """Janelas já fechadas e ainda não lidas."""
        return [
            w for w in SchemasConstants.WINDOW_DAYS if w not in self.readings and today >= self.due_date(w)
        ]

    def upcoming(self, today: date) -> list[Window]:
        return [
            w for w in SchemasConstants.WINDOW_DAYS if w not in self.readings and today < self.due_date(w)
        ]

    @model_validator(mode="after")
    def _readings_after_window(self) -> Self:
        for window, reading in self.readings.items():
            if reading.read_at < (due := self.due_date(window)):
                raise ValueError(f"leitura {window} em {reading.read_at}: a janela só fecha em {due}")
        return self
