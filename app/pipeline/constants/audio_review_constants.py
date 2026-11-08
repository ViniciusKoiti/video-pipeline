"""Constantes da conferência de áudio; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class AudioReviewConstants:
    # acima disto a sonda de CPU diz máquina limitada, e a medida do earshot não vale
    CPU_LIMIT_S: Final = 0.3
    # o earshot não mede ataque colado no começo do arquivo
    MIN_ONSET_S: Final = 0.25
