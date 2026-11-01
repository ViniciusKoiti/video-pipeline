from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class SceneAudio:
    """O que a legenda precisa de uma cena: onde ela começa no episódio, a fala e o áudio medido."""

    start_ms: int
    duration_ms: int
    narration: str
    silences_ms: Sequence[tuple[int, int]]  # silêncios internos do WAV (início, fim), em ms da cena
