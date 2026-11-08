from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SpeechRequest:
    text: str
    out_path: Path  # WAV
    language: str = "en"  # "en" | "pt-BR" (ADR 008); escolhe sotaque e voz padrão
    voice: str | None = None  # None = voz configurada para o idioma
    lexicon: Mapping[str, str] = field(default_factory=dict)  # glossário: palavra -> fonemas (§9)
    delivery: str = "neutral"  # entrega da fala (ADR 022): "neutral" ou "hook"; quem não souber ignora
