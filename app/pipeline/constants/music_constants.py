"""Constantes de music; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class MusicConstants:
    # fundos novos por minuto de vídeo, em média: troca só nas viradas
    MAX_BED_CHANGES_PER_MINUTE: Final[float] = 1.0
    MIN_CUE_MS: Final[int] = 1000
    # prefixo do id das faixas da YouTube Audio Library no catálogo
    ID_PREFIX: Final[str] = "ytal-"
    LIBRARY_URL: Final[str] = "https://www.youtube.com/audiolibrary"
