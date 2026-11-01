from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class GeminiTTSSettings(_Model):
    """Gemini TTS na camada gratuita (ADR 012); a chave fica no `.env` (GEMINI_API_KEY)."""

    model: str = "gemini-3.8-flash-tts"
    voices: dict[str, str] = Field(default_factory=lambda: {"pt-BR": "Charon"})  # idioma -> voz
    styles: dict[str, str] = Field(default_factory=dict)  # idioma -> direção de fala (speech_metadata.style)
    requests_per_minute: int = Field(default=3, gt=0)  # limite da camada gratuita
    chars_per_second: float = Field(default=13.0, gt=0)
