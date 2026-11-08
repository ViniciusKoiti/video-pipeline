from __future__ import annotations

from pydantic import Field, field_validator

from app.pipeline.models.episode_format import EpisodeFormat
from app.settings.models._settings_model import _Model


class ProviderChoice(_Model):
    text: str
    tts: str  # voz dos rascunhos e das prévias de revisão
    tts_final: str | None = None  # voz do vídeo final e do vídeo-régua (ADR 012); None = a mesma de `tts`
    image_gen: str
    archives: list[str] = Field(min_length=1)  # ordem da cascata (§8)
    aligner: str
    word_aligner: str = "groq"  # palavras com tempo para a legenda palavra a palavra (ADR 023)
    render: dict[EpisodeFormat, str]  # motor por formato do episódio (ADR 001)
    store: str
    review: str

    @field_validator("render")
    @classmethod
    def _documentary_has_engine(cls, value: dict[EpisodeFormat, str]) -> dict[EpisodeFormat, str]:
        if EpisodeFormat.ARCHIVAL_DOCUMENTARY not in value:
            raise ValueError("render precisa de um motor para archival_documentary")
        return value
