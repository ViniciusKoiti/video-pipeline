from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImageOrder:
    """Um pedido do `pedidos.json` do `vp imagens`; o `id` vira o nome do arquivo."""

    id: str
    prompt: str
    refs: tuple[Path, ...] = ()  # imagens de referência, já resolvidas pela pasta do pedidos.json
    scene: str | None = None  # "S03": conta no teto de imagens por cena (§6)
