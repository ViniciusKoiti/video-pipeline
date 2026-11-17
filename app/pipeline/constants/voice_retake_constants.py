"""Constantes de voice_retake; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class VoiceRetakeConstants:
    REJECTED_DIR: Final[str] = "tomadas-recusadas"
    # cópias da fala bruta, que começam com o nome dela (ADR 054, 060)
    COPY_DIRS: Final = ("leveled", "paced")
    STAMP: Final[str] = "%Y-%m-%d-%H%M%S"
