"""Constantes de music; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class MusicConstants:
    # fundos novos por minuto de vídeo, em média: troca só nas viradas
    MAX_BED_CHANGES_PER_MINUTE: Final[float] = 1.0
    MIN_CUE_MS: Final[int] = 1000
    # cauda só de trilha depois da última fala, para a tela final do YouTube (que dura de 5 a 20 s)
    MAX_END_TAIL_MS: Final[int] = 20_000
    # prefixo do id das faixas da YouTube Audio Library no catálogo
    ID_PREFIX: Final[str] = "ytal-"
    LIBRARY_URL: Final[str] = "https://www.youtube.com/audiolibrary"
