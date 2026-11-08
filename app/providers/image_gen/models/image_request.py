from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImageRequest:
    prompt: str
    out_path: Path
    width: int = 1024
    height: int = 1024
    steps: int = 4
    seed: int | None = None
