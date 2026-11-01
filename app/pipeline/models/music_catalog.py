from __future__ import annotations

from typing import Self

from pydantic import model_validator

from app.pipeline.models._schemas_types import _unique
from app.pipeline.models.model import Model
from app.pipeline.models.music_track import MusicTrack


class MusicCatalog(Model):
    """`data/music/catalog.json`: as faixas que o diretor musical pode usar (ADR 030)."""

    tracks: list[MusicTrack] = []

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        _unique([t.asset_id for t in self.tracks], "faixas do catálogo")
        return self

    def by_id(self) -> dict[str, MusicTrack]:
        return {t.asset_id: t for t in self.tracks}
