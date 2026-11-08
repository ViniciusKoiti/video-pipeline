"""Constantes de host; dados fixos sem I/O."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import Final


class HostConstants:
    # dentro da pasta do episódio, que é a pasta pública do render e fica fora do Git
    SPRITES_DIR: Final[str] = "host/dono"
    # o vocabulário do `<Host>` do motion-kit
    VISEMES: Final = ("rest", "mbp", "ei", "a", "ou", "fv")
    # de onde veio o desenho: autor, gerador e licença (§2.3)
    ORIGIN_FILE: Final[str] = "origem.json"
    MANIFEST_FILE: Final[str] = "sprites.json"
    # dentro de `video/`
    KIT_CLI: Final = Path("node_modules/@viniciusk/motion-kit/bin/motion-kit.mjs")
    POINT_SHOT_KINDS: Final = frozenset(("number", "compare", "calculation", "receipt", "chart"))
    POINT_MS: Final[int] = 1500
    DELIVERY_EXPRESSIONS: Final = MappingProxyType({"hook": "raised", "turn": "furrow"})
    GESTURE_CYCLE: Final = ("rest", "open")
    GESTURE_EVERY: Final[int] = 21
