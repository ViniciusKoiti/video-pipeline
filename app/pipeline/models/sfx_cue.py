from __future__ import annotations

from pydantic import Field

from app.pipeline.constants.sfx_constants import SfxConstants
from app.pipeline.models.model import Model


class SfxCue(Model):
    """Um efeito: o som do kit no momento de uma cena. O momento é o começo da cena, mais a posição de `text`
    na fala (quando há), mais `offset_s`."""

    sound: str
    scene: str
    text: str | None = None
    offset_s: float = 0.0
    gain_db: float = Field(default=0.0, le=SfxConstants.MAX_GAIN_DB)
    note: str | None = None  # o que acontece na tela nesse momento
