from __future__ import annotations

from app.pipeline.models._schemas_types import EpisodeId
from app.pipeline.models.model import Model


class TranslationLink(Model):
    derived_from: EpisodeId
    language: str
    source_language: str
