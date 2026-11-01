from __future__ import annotations

from typing import Literal

Rotulo = Literal["SUSTENTA", "DIVERGE", "SEM_SUPORTE", "EXAGERO"]


EXPECTED: dict[str, Rotulo] = {
    "real": "SUSTENTA",
    "numero": "DIVERGE",
    "trecho_alheio": "SEM_SUPORTE",
    "superlativo": "EXAGERO",
}
