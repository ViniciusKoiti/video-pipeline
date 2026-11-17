from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class WhisperLocalSettings(_Model):
    """Whisper local pelo `transformers` (ADR 062): reconhece a fala para a conferência depois da voz. O
    modelo vem do cache do Hugging Face (`hf download <modelo>` uma vez); sem ele, o adaptador para."""

    model: str = "openai/whisper-small"  # apache-2.0; ~1 GB de pesos
    num_threads: int = Field(default=8, gt=0)
    chunk_length_s: float = Field(default=30.0, gt=0)
