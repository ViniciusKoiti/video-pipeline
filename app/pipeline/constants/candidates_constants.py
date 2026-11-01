"""Constantes da busca de candidatos visuais; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class CandidatesConstants:
    ORIENTATIONS: Final = ("landscape", "portrait")
    DEFAULT_MEDIA: Final = ("video",)
    # candidatos por chamada ao banco, para a triagem humana escolher até 2 por plano
    DEFAULT_LIMIT: Final[int] = 5
