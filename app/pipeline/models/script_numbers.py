from __future__ import annotations

from dataclasses import dataclass, field

from app.pipeline.models.citation import Citation
from app.pipeline.models.shot_timing import ShotTiming


@dataclass(frozen=True)
class ScriptNumbers:
    scenes: int
    shots: int
    text_shots: int
    pauses: int
    words: int
    duration_ms: float
    voce: int
    voce_scenes: int
    voce_closing: int
    opening: tuple[int, float]  # planos que começam no primeiro décimo, e a duração desse décimo (ms)
    rest: tuple[int, float]
    rhythm_alerts: list[ShotTiming]
    citations: list[Citation]
    assets_by_use: dict[str, list[str]]  # ativo -> cenas, na ordem da primeira aparição
    unused_assets: list[str]
    measures: dict[str, float] = field(default_factory=dict)  # as medidas na unidade do nicho
