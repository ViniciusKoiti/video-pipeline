from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FitRow:
    """Uma cena depois de `MotionContent.fitted`: a duração do JSON e a que a fala pede."""

    scene: str
    before: float
    after: float
    spoken: float | None  # segundos de fala, ou None se a cena não tem fala
