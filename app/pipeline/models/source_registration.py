from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models.source import Source


@dataclass(frozen=True)
class SourceRegistration:
    source: Source
    created: bool  # False: já estava registrada (mesma URL ou mesmo texto declarado); nada foi escrito
