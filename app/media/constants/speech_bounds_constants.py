"""Constantes dos limites da fala num WAV; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class SpeechBoundsConstants:
    # A voz clonada devolve silêncio nas pontas do WAV (até 1 s antes da fala, em 2026-10-25): a fala é o
    # trecho entre os silêncios das pontas, com uma respiração de cada lado.
    NOISE_DB: Final = -35
    EDGE_SILENCE_S: Final = 0.15
    BREATH_S: Final = 0.08
    # a ponta do arquivo: um silêncio que começa (ou termina) a menos de 50 ms dela vale como a ponta
    EDGE_TOLERANCE_S: Final = 0.05
    SILENCE_START: Final = re.compile(r"silence_start: (-?[\d.]+)")
    SILENCE_END: Final = re.compile(r"silence_end: ([\d.]+)")
