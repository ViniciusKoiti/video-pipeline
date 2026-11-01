from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class GroqWhisperSettings(_Model):
    """Whisper da Groq na camada gratuita, só para o tempo das palavras da legenda (ADR 023)."""

    model: str = "whisper-large-v3-turbo"
    timeout_s: float = Field(default=120.0, gt=0)
