from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkippedArchive:
    """Um banco da cascata que não entrou, e por quê (sem adapter, chave ausente)."""

    name: str
    reason: str
