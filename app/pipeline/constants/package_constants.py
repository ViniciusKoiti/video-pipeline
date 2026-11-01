"""Constantes do pacote de vídeo e texto do gate 4; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class PackageConstants:
    VIDEO: Final[str] = "renders/final.mp4"
    TEXT: Final[str] = "legenda-post.txt"
    # o marcador do pacote: `writing` enquanto grava, `complete` só depois do último arquivo
    MARKER: Final[str] = "renders/pacote.json"
    EPISODE_ID: Final = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
