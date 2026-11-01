"""Constantes da biblioteca de falas e do narrador; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class VoiceConstants:
    # vozes clonadas: no Short, a entrega entra na chave pelo nome, no formato de hoje (ADR 049)
    CLONED: Final = ("chatterbox", "chatterbox_modal")
    NEUTRAL: Final[str] = "neutral"
    LEGACY_DELIVERY: Final[str] = "|entrega:{name}"
    # tamanho do hash no nome do WAV
    DIGEST_CHARS: Final[int] = 10
