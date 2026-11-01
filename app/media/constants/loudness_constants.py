"""Constantes de loudness; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class LoudnessConstants:
    # volume final de um vídeo com trilha
    TARGET_LUFS: Final = -14.0
    TOLERANCE_LU: Final[float] = 1.5
    _INTEGRATED: Final = re.compile("I:\\s+(-?\\d+(?:\\.\\d+)?) LUFS")
    INTENSITY_STEPS: Final = (-30.0, -24.0, -19.0, -15.0)
