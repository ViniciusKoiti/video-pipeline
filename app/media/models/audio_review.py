from __future__ import annotations

from dataclasses import dataclass

from app.media.models.cue_sync import CueSync


@dataclass(frozen=True)
class AudioReview:
    duration_s: float
    integrated_lufs: float  # BS.1770, mono contado nos dois lados: o número que o YouTube usa
    true_peak_dbtp: float
    tempo_bpm: float | None
    pulse_clarity: float | None  # < 0,15 = sem batida que preste (o earshot não monta grade)
    cues: list[CueSync]
    median_abs_offset_ms: float | None
    chance_within_tolerance: float | None  # quantos cortes teriam um ataque perto por acaso

    @property
    def has_beat(self) -> bool:
        return self.pulse_clarity is not None and self.pulse_clarity >= 0.15
