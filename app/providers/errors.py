"""Falhas de provedor. O pipeline converte qualquer `ProviderError` em `needs_review` só na cena
afetada (§2.1, `app.pipeline.failures`); outras exceções são bugs e interrompem a execução."""

from __future__ import annotations

from typing import ClassVar


class ProviderError(Exception):
    reason: ClassVar[str] = "provider_error"

    def __init__(self, provider: str, message: str) -> None:
        super().__init__(f"{provider}: {message}")
        self.provider = provider


class QuotaExhausted(ProviderError):
    reason = "quota_exhausted"


class ModelUnavailable(ProviderError):
    """Modelo ausente ou aposentado. Nunca trocar de modelo sozinho (§2.1, §8)."""

    reason = "model_unavailable"


class LicenseUnknown(ProviderError):
    reason = "license_unknown"


class InvalidOutput(ProviderError):
    """Resposta fora do schema pedido (ex.: JSON do LLM que não valida)."""

    reason = "invalid_output"


class PaidApiBlocked(ProviderError):
    reason = "paid_api_blocked"
