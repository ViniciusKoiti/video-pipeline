from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from app.settings.constants.settings_constants import SettingsConstants
from app.settings.models._settings_model import _Model

Delivery = Literal["hook", "turn", "invite", "neutral", "calm"]  # as entregas da ADR 022


class AzureSpeechSettings(_Model):
    """Azure Speech na camada gratuita F0 (ADR 058); chave e região ficam no `.env`
    (AZURE_SPEECH_KEY, AZURE_SPEECH_REGION)."""

    region: str | None = None  # só do `.env`: a região do recurso (ex.: brazilsouth)
    tier: str = "F0"  # camada do recurso no portal; fora de F0 a síntese é cobrada e fica barrada (§2.1)
    voices: dict[str, str] = Field(default_factory=lambda: {"pt-BR": "pt-BR-AntonioNeural"})  # idioma -> voz
    output_format: Literal[
        "riff-24khz-16bit-mono-pcm", "riff-48khz-16bit-mono-pcm", "riff-44100hz-16bit-mono-pcm"
    ] = "riff-24khz-16bit-mono-pcm"
    rate: float = Field(default=1.0, ge=0.5, le=2.0)  # multiplicador do `prosody rate`; 1 = sem a tag
    pause_ms: int = Field(default=500, ge=0, le=20000)  # `<break>` no lugar de cada `<short pause>` (ADR 015)
    requests_per_minute: int = Field(default=20, gt=0)  # limite da F0: 20 chamadas por 60 s
    chars_per_second: float = Field(default=15.0, gt=0)  # provisório, sem medida; só vale como voz final
    # fator da velocidade por entrega da cena (ADR 022; emenda de 2026-11-16 da ADR 058): multiplica `rate`;
    # entrega sem fator fala em `rate`
    delivery: dict[Delivery, float] = Field(default_factory=dict)
    # marca de emoção do roteiro -> estilo do `mstts:express-as` (ADR 063); voz sem estilo ignora
    styles: dict[str, str] = Field(default_factory=dict)
    # glossário: "ipa" põe `<phoneme>` (vozes neurais); "fala" manda o texto com a grafia da fala
    # (voz MAI, ADR 063)
    pronunciation: Literal["ipa", "fala"] = "ipa"

    @field_validator("delivery")
    @classmethod
    def _factors_in_range(cls, value: dict[Delivery, float]) -> dict[Delivery, float]:
        low, high = SettingsConstants.AZURE_DELIVERY_FACTOR_RANGE
        wrong = sorted(name for name, factor in value.items() if not low <= factor <= high)
        if wrong:
            raise ValueError(f"fator de entrega fora de {low:g} a {high:g}: {', '.join(wrong)}")
        return value
