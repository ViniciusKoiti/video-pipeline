from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AffiliateUpdate:
    """O resultado de pôr o bloco de livros na descrição: o bloco, o arquivo e se ele mudou."""

    block: str
    path: Path
    changed: bool
