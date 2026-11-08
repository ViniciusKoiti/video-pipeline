from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.models.voice_key import VoiceKey
from app.providers.tts.base import SpeechRequest


@dataclass(frozen=True)
class PlannedSpeech:
    """Uma fala que falta: a linha, a chave dela e o pedido pronto para o TTS."""

    line: SpeechLine
    key: VoiceKey
    request: SpeechRequest
