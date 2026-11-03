from __future__ import annotations

from typing import Final


class VoiceLevelConstants:
    TARGET_LUFS: Final[float] = -16.0
    TRUE_PEAK_DBTP: Final[float] = -1.5
    LRA: Final[int] = 11
    SAMPLE_RATE: Final[int] = 48000
    VERSION: Final[int] = 1
    TOLERANCE_LU: Final[float] = 0.75
    PEAK_TOLERANCE_DB: Final[float] = 0.3
    DURATION_TOLERANCE_MS: Final[int] = 20
    REASON: Final[str] = "voice_level_failed"
    DIGEST_CHARS: Final[int] = 12
    DIRECTORY: Final[str] = "leveled"

