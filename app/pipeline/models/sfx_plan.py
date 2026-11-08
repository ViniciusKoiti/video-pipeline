from __future__ import annotations

from app.pipeline.models.model import Model
from app.pipeline.models.sfx_cue import SfxCue


class SfxPlan(Model):
    """`sfx.json`: os efeitos de um vídeo, escritos por quem monta o Short; o código confere e coloca."""

    cues: list[SfxCue]
