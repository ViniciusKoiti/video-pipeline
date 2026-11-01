from __future__ import annotations

from app.pipeline.models.model import Model


class NarrationLine(Model):
    scene: str | None = None  # id da cena do vídeo; None = fala de um plano fora do JSON
    text: str
    delivery: str | None = None  # hook | turn | calm | invite (ADR 022)
