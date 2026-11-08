"""Constantes de narration; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class NarrationConstants:
    PAUSE_TAG: Final[str] = "<short pause>"
    # reservada ao lote de cenas do Gemini (ADR 012), nunca dentro da narração
    LONG_PAUSE_TAG: Final[str] = "<long pause>"
    # ≈0,75 s a 13 caracteres por segundo; no teste de 2026-10-05 as pausas ficaram em 0,5–1,1 s
    PAUSE_CHARS: Final[int] = 10
    _PAUSE: Final = re.compile("[ \\t]*<short pause>[ \\t]*")
    _WELL_PLACED: Final = re.compile("(?<=\\S) <short pause> (?=\\S)")
    _ANY_TAG: Final = re.compile("<[^<>]*>")
