from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImageRequest:
    prompt: str
    out_path: Path  # o adaptador pode trocar a extensão pela do arquivo que recebeu (ADR 065)
    width: int = 1024
    height: int = 1024
    steps: int = 4
    seed: int | None = None
    refs: tuple[Path, ...] = ()  # imagens de referência anexadas ao pedido (folha do boneco, estilo)
