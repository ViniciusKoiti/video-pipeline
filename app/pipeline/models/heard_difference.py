from __future__ import annotations

from typing import Literal

from app.pipeline.models.model import Model


class HeardDifference(Model):
    """Um trecho em que o reconhecedor ouviu outra coisa que o roteiro (ADR 062). `kind`: `termo` quando o
    trecho tem um termo do glossário, `palavra` nos outros. O tempo é do WAV da cena, em ms."""

    scene_id: str
    kind: Literal["termo", "palavra"]
    expected: str  # como o roteiro escreve
    heard: str  # como o reconhecedor escreveu ("" se não ouviu nada)
    spoken_as: str = ""  # a `fala` do glossário, quando é termo
    start_ms: int
    end_ms: int
