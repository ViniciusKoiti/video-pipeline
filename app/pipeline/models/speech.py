from __future__ import annotations

from app.pipeline.models.model import Model


class Speech(Model):
    """A fala de uma cena na junção: começa no começo da cena e dura `seconds`."""

    seconds: float
