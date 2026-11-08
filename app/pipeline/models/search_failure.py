from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchFailure:
    """Uma consulta que um banco não respondeu (cota, serviço, resposta inválida): não é "sem resultado"."""

    bank: str
    query: str
    reason: str  # `ProviderError.reason`: quota_exhausted, invalid_output, provider_error...
    detail: str
