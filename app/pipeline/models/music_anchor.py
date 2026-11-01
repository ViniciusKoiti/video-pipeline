from __future__ import annotations

from pydantic import Field

from app.pipeline.models._schemas_types import SceneId
from app.pipeline.models.model import Model


class MusicAnchor(Model):
    """Ponto da narração, como a âncora de um plano (ADR 008): o trecho dentro da cena. Sem `text`, a entrada
    vale no começo da cena e a saída, no fim dela."""

    scene: SceneId
    text: str | None = Field(default=None, min_length=1)
