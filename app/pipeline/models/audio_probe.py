from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AudioProbe:
    """As medidas de uma faixa (ffprobe e loudness), injetadas: o serviço e os testes não rodam ffmpeg."""

    duration_ms: Callable[[Path], int]
    lufs: Callable[[Path], float]
    intensity: Callable[[float], int]  # da loudness integrada para 1 a 5
