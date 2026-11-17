"""Fábricas das portas de alinhamento ao áudio: Groq (legenda palavra a palavra, ADR 023) e Whisper local
(conferência da fala, ADR 062). Saíram de `app/bootstrap/__init__.py` pelo gate de tamanho."""

from __future__ import annotations

from app.bootstrap.secrets import secret
from app.providers.alignment.base import WordAligner
from app.settings import Settings


def groq_words(settings: Settings) -> WordAligner:
    from app.providers.alignment.groq import GroqWordAligner

    whisper = settings.groq_whisper
    key = secret(settings, "GROQ_API_KEY")
    return GroqWordAligner(key, model=whisper.model, timeout_s=whisper.timeout_s)


def whisper_local(settings: Settings) -> WordAligner:
    from app.providers.alignment.whisper_local import WhisperLocalWordAligner

    local = settings.whisper_local
    return WhisperLocalWordAligner(
        model=local.model, num_threads=local.num_threads, chunk_length_s=local.chunk_length_s
    )
