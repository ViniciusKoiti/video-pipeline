from __future__ import annotations

from typing import Self

from pydantic import model_validator

from app.pipeline.models._schemas_types import EpisodeId, _unique
from app.pipeline.models.model import Model
from app.pipeline.models.source import Source


class SourcesManifest(Model):
    """O mínimo de 2 fontes independentes fica para o gate 1: independência é julgamento humano."""

    episode_id: EpisodeId
    sources: list[Source]

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([s.id for s in self.sources], "ids de fonte")
        return self
