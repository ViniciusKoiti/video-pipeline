"""Portas de alinhamento ao áudio aprovado (§9): legenda por frase e palavras reconhecidas com tempo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.providers.base import ProviderInfo


@dataclass(frozen=True)
class Cue:
    start_ms: int
    end_ms: int
    text: str


class SubtitleAligner(Protocol):
    info: ProviderInfo

    def align(self, text: str, audio: Path) -> list[Cue]: ...


@dataclass(frozen=True)
class TimedWord:
    """Uma palavra reconhecida no áudio, com o tempo em ms do arquivo. O texto é o do reconhecedor, não o do
    roteiro: quem usa casa os dois (`app.media.word_captions`)."""

    text: str
    start_ms: int
    end_ms: int


class WordAligner(Protocol):
    """Reconhece as palavras de um áudio com o tempo de cada uma (ADR 023). `prompt` é o texto esperado, que
    ajuda o reconhecedor a escrever nomes e termos como no roteiro."""

    info: ProviderInfo

    def recognize_words(self, audio: Path, language: str, prompt: str = "") -> list[TimedWord]: ...
