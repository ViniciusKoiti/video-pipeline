from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.pipeline.models.generation import Generation


@dataclass(frozen=True)
class GeneratedImage:
    path: Path
    generator: str  # quem gerou: modelo da API ou site da tela ("gemini")
    # Semente e passos de um modelo reproduzível; None no gerador sem seed, como a tela de um site (ADR 065).
    generation: Generation | None = None
    origin: str = ""  # onde reabrir a imagem depois (a conversa do site); vazio quando não há
