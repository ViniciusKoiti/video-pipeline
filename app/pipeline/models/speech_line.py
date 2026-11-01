from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpeechLine:
    """Uma fala a gerar: a cena do longo ou a linha da narração do Short."""

    id: str  # "S01", ou "fora-3" para fala sem cena no JSON do motion-video
    text: str  # o texto do roteiro, com `<short pause>`
    delivery: str = "neutral"
