"""Constantes de envelope; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class EnvelopeConstants:
    # o nível que vale 1: picos isolados não achatam o resto da cena
    PERCENTILE: Final[float] = 0.95
