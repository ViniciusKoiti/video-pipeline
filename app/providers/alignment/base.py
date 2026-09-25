"""Porta de alinhamento de legendas ao áudio aprovado (§9)."""

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
