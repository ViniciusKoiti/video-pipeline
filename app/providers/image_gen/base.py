"""Porta de geração de imagem para lacunas (§8). Estimar o custo sempre antes de gerar."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.providers.base import ProviderInfo
from app.providers.image_gen.models.cost_estimate import CostEstimate as CostEstimate
from app.providers.image_gen.models.generated_image import GeneratedImage as GeneratedImage
from app.providers.image_gen.models.image_request import ImageRequest as ImageRequest


class ImageGenProvider(Protocol):
    info: ProviderInfo

    def estimate_cost(self, request: ImageRequest) -> CostEstimate: ...

    def generate_image(self, request: ImageRequest) -> GeneratedImage: ...

    def close(self) -> None: ...  # libera conexão ou navegador; chamar uma vez, ao fim da rodada


@runtime_checkable
class PageMapper(Protocol):
    """Gerador operado por uma página: lista o que cada seletor encontra (`vp imagens mapear`, ADR 065)."""

    def map_page(self) -> list[str]: ...
