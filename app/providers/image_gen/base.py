"""Porta de geração de imagem para lacunas (§8). Estimar o custo sempre antes de gerar."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.pipeline.schemas import Generation
from app.providers.base import ProviderInfo


@dataclass(frozen=True)
class ImageRequest:
    prompt: str
    out_path: Path
    width: int = 1024
    height: int = 1024
    steps: int = 4
    seed: int | None = None


@dataclass(frozen=True)
class CostEstimate:
    units: float
    unit: str  # ex.: "neurons"
    usd: float  # > 0 é recusado enquanto ALLOW_PAID_API=false


@dataclass(frozen=True)
class GeneratedImage:
    path: Path
    generation: Generation


class ImageGenProvider(Protocol):
    info: ProviderInfo

    def estimate_cost(self, request: ImageRequest) -> CostEstimate: ...

    def generate_image(self, request: ImageRequest) -> GeneratedImage: ...
