"""Constantes de music; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class MusicConstants:
    # fundos novos por minuto de vídeo, em média: troca só nas viradas
    MAX_BED_CHANGES_PER_MINUTE: Final[float] = 1.0
    MIN_CUE_MS: Final[int] = 1000
