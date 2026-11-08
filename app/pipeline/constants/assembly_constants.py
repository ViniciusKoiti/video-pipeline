"""Constantes da montagem e do render do episódio; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class AssemblyConstants:
    EPISODE: Final[str] = "episode.json"
    # a prévia e o final são arquivos diferentes: o gate 4 carimba um ou o outro (#120), nunca os dois como um
    PREVIEW: Final[str] = "renders/preview.mp4"
    FINAL: Final[str] = "renders/final.mp4"
