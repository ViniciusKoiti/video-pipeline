"""Porta de narração. A duração do WAV é medida depois com ffprobe, nunca confiada ao adapter (§9)."""

from __future__ import annotations

from typing import Protocol

from app.providers.base import ProviderInfo
from app.providers.tts.models.speech_request import SpeechRequest as SpeechRequest
from app.providers.tts.models.speech_result import SpeechResult as SpeechResult


class TTSProvider(Protocol):
    info: ProviderInfo

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult: ...
