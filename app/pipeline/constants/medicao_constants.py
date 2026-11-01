"""Constantes de medicao; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class MedicaoConstants:
    MEDICAO_FILE: Final[str] = "medicao.json"
    # strings da tela que contam
    TEXT_KEYS: Final = frozenset(("text", "title", "sub", "label", "highlight"))
    _NUMBER: Final = re.compile("\\d+(?:[.,]\\d+)?")
    DEFAULT_TOLERANCE: Final[float] = 0.01
