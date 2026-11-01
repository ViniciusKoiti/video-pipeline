from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.pipeline.models.generation import Generation


@dataclass(frozen=True)
class GeneratedImage:
    path: Path
    generation: Generation
