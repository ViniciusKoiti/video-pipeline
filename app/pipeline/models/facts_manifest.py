from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import EpisodeId, Language, _unique
from app.pipeline.models.fact import Fact
from app.pipeline.models.model import Model


class FactsManifest(Model):
    """Fichas de fatos: a única base do roteiro. Cada fato traz a citação literal que o sustenta."""

    episode_id: EpisodeId
    language: Language
    facts: list[Fact] = Field(min_length=1)
    open_questions: list[str] = []  # perguntas que prenderiam o público e que as fontes não respondem

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([f.id for f in self.facts], "ids de fato")
        return self
