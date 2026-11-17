from __future__ import annotations

from app.pipeline.models.heard_difference import HeardDifference
from app.pipeline.models.model import Model


class SceneHearing(Model):
    """O que o reconhecedor ouviu numa cena e onde isso foge do roteiro (ADR 062)."""

    scene_id: str
    wav: str  # relativo à pasta do episódio
    heard: str
    word_error_rate: float  # palavras trocadas, faltando ou a mais, sobre as palavras do roteiro
    differences: list[HeardDifference] = []
