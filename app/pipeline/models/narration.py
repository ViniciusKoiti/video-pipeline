from __future__ import annotations

from app.pipeline.models.model import Model
from app.pipeline.models.narration_line import NarrationLine


class Narration(Model):
    language: str
    lines: list[NarrationLine]
