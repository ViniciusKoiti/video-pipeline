from __future__ import annotations

from pydantic import Field

from app.pipeline.constants.music_constants import MusicConstants
from app.pipeline.models._schemas_types import EpisodeId
from app.pipeline.models.model import Model
from app.pipeline.models.music_cue import MusicCue


class MusicPlan(Model):
    """`music.json`: o plano da trilha, escrito pelo agente diretor-musical (ADR 030)."""

    episode_id: EpisodeId
    cues: list[MusicCue] = []
    # segundos só de trilha depois da última fala (tela final do YouTube): o fundo que chega ao fim da última
    # cena continua por esse tempo (emenda de 2026-11-23 da ADR 030)
    end_tail_ms: int = Field(default=0, ge=0, le=MusicConstants.MAX_END_TAIL_MS)
