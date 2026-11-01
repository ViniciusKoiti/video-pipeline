"""Constantes de earshot; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class EarshotConstants:
    # acima disso o encoder já passou do teto; o loudnorm pede −1,5
    MAX_TRUE_PEAK_DBTP: Final = -1.0
    # um quadro a 25 fps; o earshot usa o mesmo limiar nos `--cues`
    SYNC_TOLERANCE_MS: Final[int] = 40
