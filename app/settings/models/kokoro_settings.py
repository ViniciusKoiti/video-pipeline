from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class KokoroSettings(_Model):
    voices: dict[str, str] = Field(min_length=1)  # idioma -> voz (ADR 008)
    num_threads: int = Field(default=8, gt=0)
    chars_per_second: float = Field(default=15.0, gt=0)  # ritmo da voz, para estimar a cena antes do WAV
    pause_ms: int = Field(default=300, ge=0)  # silêncio no lugar de cada `<short pause>` (ADR 015)
