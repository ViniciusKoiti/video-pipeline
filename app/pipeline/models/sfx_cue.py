from __future__ import annotations

from pydantic import Field

from app.pipeline.constants.sfx_constants import SfxConstants
from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class SfxCue(Model):
    """Um efeito: o som do kit no momento de uma cena. O momento é o começo da cena, mais a posição de `text`
    na fala (quando há), mais `offset_s`. Deslocamento e ganho são números finitos."""

    sound: NonEmpty
    scene: NonEmpty
    text: NonEmpty | None = None
    offset_s: float = Field(default=0.0, allow_inf_nan=False)
    gain_db: float = Field(default=0.0, le=SfxConstants.MAX_GAIN_DB, allow_inf_nan=False)
    note: str | None = None  # o que acontece na tela nesse momento
