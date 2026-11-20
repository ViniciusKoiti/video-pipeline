"""Composição da voz do Azure Speech (ADR 058): confere a chave e a região do `.env` e monta o adapter.

O adapter é importado dentro da fábrica, como as outras do registro."""

from __future__ import annotations

from app.bootstrap.registry import ConfigurationError
from app.providers.tts.base import TTSProvider
from app.settings import Settings


def build_azure_speech(settings: Settings) -> TTSProvider:
    from app.providers.tts.azure_speech import AzureSpeechTTS
    from app.providers.tts.constants.azure_speech_constants import AzureSpeechConstants

    azure, key = settings.azure_speech, settings.secrets.azure_speech_key
    if key is None:
        raise ConfigurationError("AZURE_SPEECH_KEY ausente no .env")
    if not azure.region:
        raise ConfigurationError("AZURE_SPEECH_REGION ausente no .env")
    if not AzureSpeechConstants.REGION.fullmatch(azure.region):  # entra no nome do host
        raise ConfigurationError("AZURE_SPEECH_REGION inválida: use a região do recurso (ex.: brazilsouth)")
    delivery_rates: dict[str, float] = {name: factor for name, factor in azure.delivery.items()}
    return AzureSpeechTTS(
        key.get_secret_value(), azure.region, voices=azure.voices, output_format=azure.output_format,
        rate=azure.rate, delivery_rates=delivery_rates, pause_ms=azure.pause_ms,
        requests_per_minute=azure.requests_per_minute, tier=azure.tier,
        styles=azure.styles, ipa=azure.pronunciation == "ipa",
    )
