"""Constantes de gemini; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class GeminiConstants:
    API: Final[str] = "https://generativelanguage.googleapis.com/v1beta/interactions"
    # a fala mais longa do teste (188 caracteres) levou 27,5 s
    TIMEOUT_S: Final[float] = 90.0
    # tempo a mais por caractere num lote (~3 s de espera por segundo de fala)
    SECONDS_PER_CHAR: Final = 3 / 13
    # marca da documentação; em inglês mesmo com texto em português
    SCENE_BREAK: Final[str] = " <long pause> "
    # e status None: tempo esgotado ou rede
    TRANSIENT: Final = frozenset((429, 500, 503))
    # folga sobre 60 / chamadas por minuto
    MARGIN_S: Final[float] = 1.0
