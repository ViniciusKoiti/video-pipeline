from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Report:
    with_words: list[str]  # cenas com palavra a palavra
    without: list[str]  # cenas sem reconhecimento (ficam na legenda por frase)
    unmatched: int  # palavras do roteiro com tempo dividido
