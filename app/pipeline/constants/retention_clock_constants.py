"""Constantes de retention_clock; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class RetentionClockConstants:
    # Abaixo disso o vídeo é Short ou Reel, e o relógio não confere nada.
    LONG_VIDEO_SECONDS: Final[float] = 240.0
    # A cena que fecha a promessa termina até aqui (regra do dono, 2026-11-16).
    PROMISE_BY_SECONDS: Final[float] = 30.0
    # Janela do gancho de retomada ou da virada: cerca de 60% saem até os 2 min, e quem fica fica uns 3 min
    # (docs/pesquisa/retencao-idade-media-2026-11-14.md).
    REHOOK_FROM_SECONDS: Final[float] = 120.0
    REHOOK_BY_SECONDS: Final[float] = 180.0
    REHOOK_BEATS: Final = frozenset(("rehook", "turn"))
    # A fala de uma cena que é aviso (CVV, saúde) e devia estar marcada como pausa, no texto sem acento.
    PAUSE_HINTS: Final = (r"\bcvv\b", r"\bcentro de valorizacao da vida\b", r"\b188\b")
    RESEARCH: Final[str] = "docs/pesquisa/retencao-idade-media-2026-11-14.md"
