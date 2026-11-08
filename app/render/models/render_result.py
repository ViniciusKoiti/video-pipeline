from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenderResult:
    path: Path
    width: int
    height: int
    duration_ms: int
