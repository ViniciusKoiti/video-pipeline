from __future__ import annotations

from typing import Literal

from pydantic import AwareDatetime, Field

from app.pipeline.models._schemas_types import SceneId
from app.pipeline.models.episode_format import EpisodeFormat
from app.pipeline.models.model import Model


class FormatDecision(Model):
    stage: Literal["topic", "scenes"]
    recommended: EpisodeFormat
    scores: dict[EpisodeFormat, float]
    reasons: list[str] = Field(min_length=1)
    graphic_scenes_as_assets: list[SceneId] = []  # cenas para o caminho "gráfico como ativo" (etapa #42)
    input_hash: str
    decided_at: AwareDatetime
