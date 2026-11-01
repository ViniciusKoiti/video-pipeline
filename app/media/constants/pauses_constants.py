"""Constantes de pauses; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class PausesConstants:
    # abaixo disto é silêncio
    NOISE_DB: Final = -40
    # silêncios mais curtos nem entram na conta
    MIN_SILENCE_S: Final[float] = 0.2
    # uma fronteira entre cenas dura pelo menos isto
    MIN_BOUNDARY_S: Final[float] = 0.6
    # a fronteira mais curta é 30% maior que a pausa mais longa dentro das cenas
    MARGIN: Final[float] = 1.3
    # silêncio mantido antes da fala de cada cena (o Kokoro deixa ~0,2 s)
    LEAD_S: Final[float] = 0.2
    # silêncio mantido depois da fala
    TAIL_S: Final[float] = 0.15
