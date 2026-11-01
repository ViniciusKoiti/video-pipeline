from __future__ import annotations

from enum import StrEnum


class Naming(StrEnum):
    """Os dois formatos de nome de WAV de hoje, preservados (ADR 049)."""

    LONG = "long"  # <cena>-<provedor>-<hash>.wav
    SHORT = "short"  # <cena>-<provedor>-<idioma>-<hash>.wav: o idioma separa as duas línguas de uma cena
