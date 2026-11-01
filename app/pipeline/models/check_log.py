from __future__ import annotations

from app.pipeline.models._schemas_types import EpisodeId
from app.pipeline.models.check_entry import CheckEntry
from app.pipeline.models.model import Model


class CheckLog(Model):
    """`checagem.json`: pareceres do verificador, só acrescentados (ADR 009, emenda da cadeia de provas)."""

    episode_id: EpisodeId
    entries: list[CheckEntry] = []
