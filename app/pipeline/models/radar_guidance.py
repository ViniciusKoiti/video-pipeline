from __future__ import annotations

from typing import Literal

from app.pipeline.models._radar_radar import _Radar


class RadarGuidance(_Radar):
    about: str  # form | opening | video | engagement | theme
    trait: str
    advice: Literal["use", "avoid"]
    strength: Literal["pattern", "hint"]  # pattern: 5+ Reels de cada lado e acaso até 10%; hint: até 30%
    share_rate_with: float | None = None
    share_rate_without: float | None = None
    n_with: int
    n_without: int
    chance: float
