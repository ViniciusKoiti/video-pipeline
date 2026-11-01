from __future__ import annotations

from typing import Self

from pydantic import field_validator, model_validator

from app.pipeline.models._schemas_types import _WHEN_RE, _YEAR_RE, NonEmpty
from app.pipeline.models.model import Model


class TimelineEvent(Model):
    date: NonEmpty  # texto na tela ("7 jan. 1918", "anos 1920")
    label: NonEmpty
    when: str | None = None  # ano ou data ISO: posição na escala real (ADR 011)

    @field_validator("when", mode="before")
    @classmethod
    def _year_as_text(cls, value: object) -> object:
        return str(value) if isinstance(value, int) else value

    @model_validator(mode="after")
    def _when_matches_date(self) -> Self:
        if self.when is None:
            return self
        if not _WHEN_RE.match(self.when):
            raise ValueError(f"when {self.when!r}: use o ano (1927) ou uma data ISO (1927-03-12)")
        years = _YEAR_RE.findall(self.date)
        if years and self.when[:4] not in years:
            raise ValueError(f"when {self.when!r} não bate com o ano escrito em {self.date!r}")
        return self
