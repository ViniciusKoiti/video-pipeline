from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CaptionsReport:
    """O que a legenda por frase fez: o aviso do arquivo, os blocos, as fronteiras no tempo proporcional e os
    blocos que pedem revisão do dono (número e motivo)."""

    note: str
    blocks: int
    approximate: int
    hints: tuple[tuple[int, str], ...]
