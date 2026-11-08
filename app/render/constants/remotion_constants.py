"""Constantes de remotion; dados fixos sem I/O."""

from __future__ import annotations

from pathlib import Path
from typing import Final


class RemotionConstants:
    PROJECT: Final = Path(__file__).resolve().parents[3] / "video"
    TEMPLATE_GLOBS: Final = (
        "src/*.ts",
        "src/*.tsx",
        "src/fonts/*",
        "src/geo/*.json",
        "src/geo/*.ts",
        "render-scenes.mjs",
        "package-lock.json",
    )
    MEDIA_KINDS: Final = frozenset(("photo", "broll"))
