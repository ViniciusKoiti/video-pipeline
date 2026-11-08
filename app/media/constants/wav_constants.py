"""Constantes de wav; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class WavConstants:
    # cabeçalho RIFF/WAVE de um PCM; menos que isso não tem fala
    HEADER_BYTES: Final[int] = 44
