"""Tipos comuns a todos os provedores (ADR 006)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderInfo:
    """Identificação e custo que todo adapter declara. Custo > 0 exige ALLOW_PAID_API (§2.1)."""

    name: str
    remote: bool
    usd_per_call: float = 0.0
