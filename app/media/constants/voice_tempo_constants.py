from __future__ import annotations

from typing import Final


class VoiceTempoConstants:
    FILE: Final[str] = "voice/ritmo.json"
    NEUTRAL: Final[float] = 1.0
    # O atempo (WSOLA) perde até uma janela no fim da fala: ~32 ms medidos nas falas de 2026-11-15.
    DURATION_SLACK_MS: Final[int] = 50
