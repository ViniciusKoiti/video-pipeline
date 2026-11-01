"""O nome de WAV que os scripts de voz faziam antes do `Narrator` (RF6, ADR 049), congelado como oráculo.

O dono decidiu manter o nome dos WAVs já gerados: estas fórmulas são a especificação do nome de hoje e não
mudam. Eram o código de `montar_episodio.py` (longo) e `shorts_tec.py` (Short); os scripts passaram a usar o
`VoiceKey`, e o RF7 pode apagar os scripts sem perder a prova."""

from __future__ import annotations

import hashlib

from app.media.narration import has_pauses, split_pauses
from app.providers.tts.chatterbox import reference_hash
from app.providers.tts.constants.chatterbox_constants import ChatterboxConstants
from app.settings import Settings

CLONED = ("chatterbox", "chatterbox_modal")


def voice_fingerprint(settings: Settings, provider: str, language: str) -> str:
    """O que muda a fala gerada, além do texto: provedor, modelo, voz e direção de fala."""
    if provider == "gemini":
        gemini = settings.gemini_tts
        return f"gemini|{gemini.model}|{gemini.voices.get(language)}|{gemini.styles.get(language, '')}"
    if provider in CLONED:
        box = settings.chatterbox
        reference = box.reference.expanduser() if box.reference else None
        voice = reference_hash(reference) if reference and reference.is_file() else None
        return f"{provider}|{box.model}|{box.language_ids.get(language)}|{voice}"
    return f"{provider}|{settings.kokoro.voices.get(language)}"


def long_speech_tag(provider: str, text: str) -> str:
    """A fala clonada longa sai em grupos de frases (#186) e entra na chave."""
    if provider not in CLONED:
        return ""
    long = any(len(part) > ChatterboxConstants.MAX_PART_CHARS for part in split_pauses(text) or [text])
    return f"|frases{ChatterboxConstants.MAX_PART_CHARS}" if long else ""


def long_name(settings: Settings, provider: str, scene: str, text: str, delivery: str, language: str) -> str:
    """O nome no longo: o laço de `main` do `montar_episodio.py`."""
    pauses = {"kokoro": settings.kokoro.pause_ms, **dict.fromkeys(CLONED, settings.chatterbox.pause_ms)}
    pause_ms = pauses.get(provider)
    pause = f"|pausa{pause_ms}" if pause_ms is not None and has_pauses(text) else ""
    entrega = f"|entrega:{delivery}" if provider in CLONED and delivery != "neutral" else ""
    fingerprint = voice_fingerprint(settings, provider, language)
    raw = f"{fingerprint}{pause}{entrega}{long_speech_tag(provider, text)}|{text}"
    return f"{scene}-{provider}-{hashlib.sha256(raw.encode()).hexdigest()[:10]}.wav"


def short_name(
    stem: str, provider: str, fingerprint: str, delivery: str, text: str, language: str = "pt-BR"
) -> str:
    """O nome no Short: `wav_name` do `shorts_tec.py` (`stem` é a cena ou `fora-N`)."""
    tag = f"|entrega:{delivery}" if provider in CLONED and delivery != "neutral" else ""
    key = hashlib.sha256(f"{fingerprint}{tag}|{text}".encode()).hexdigest()[:10]
    return f"{stem}-{provider}-{language.lower().replace('-', '')}-{key}.wav"
