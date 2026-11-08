from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpeechResult:
    path: Path
    model: str
    voice: str
