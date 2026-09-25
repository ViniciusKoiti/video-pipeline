"""Porta de narração. A duração do WAV é medida depois com ffprobe, nunca confiada ao adapter (§9)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from app.providers.base import ProviderInfo


@dataclass(frozen=True)
class SpeechRequest:
    text: str
    out_path: Path  # WAV
    voice: str | None = None  # None = voz padrão do adapter
    lexicon: Mapping[str, str] = field(default_factory=dict)  # glossário: palavra -> fonemas (§9)


@dataclass(frozen=True)
class SpeechResult:
    path: Path
    model: str
    voice: str


class TTSProvider(Protocol):
    info: ProviderInfo

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult: ...
