from __future__ import annotations

from app.pipeline.models._schemas_types import EpisodeId
from app.pipeline.models.model import Model
from app.pipeline.models.music_cue import MusicCue


class MusicPlan(Model):
    """`music.json`: o plano da trilha, escrito pelo agente diretor-musical (ADR 030)."""

    episode_id: EpisodeId
    cues: list[MusicCue] = []
