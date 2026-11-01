"""Portas de alinhamento ao áudio aprovado (§9): legenda por frase e palavras reconhecidas com tempo."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.providers.alignment.models.cue import Cue as Cue
from app.providers.alignment.models.timed_word import TimedWord as TimedWord
from app.providers.base import ProviderInfo


class SubtitleAligner(Protocol):
    info: ProviderInfo

    def align(self, text: str, audio: Path) -> list[Cue]: ...


class WordAligner(Protocol):
    """Reconhece as palavras de um áudio com o tempo de cada uma (ADR 023). `prompt` é o texto esperado, que
    ajuda o reconhecedor a escrever nomes e termos como no roteiro."""

    info: ProviderInfo

    def recognize_words(self, audio: Path, language: str, prompt: str = "") -> list[TimedWord]: ...
