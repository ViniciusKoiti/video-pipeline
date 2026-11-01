"""Constantes de http; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class HttpConstants:
    CHUNK_BYTES: Final = 1 << 20
    USER_AGENT: Final[str] = "video-pipeline/0.1"
