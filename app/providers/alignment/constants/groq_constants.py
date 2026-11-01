"""Constantes de groq; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class GroqConstants:
    URL: Final[str] = "https://api.groq.com/openai/v1/audio/transcriptions"
    # o Whisper só usa os últimos ~224 tokens do prompt
    PROMPT_CHARS: Final[int] = 600
