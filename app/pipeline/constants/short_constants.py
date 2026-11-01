"""Constantes da montagem do Short; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class ShortConstants:
    # quanto a fala pode passar do fim da cena sem ser erro (arredondamento de quadros)
    OVERRUN_TOLERANCE_S: Final = 0.05
