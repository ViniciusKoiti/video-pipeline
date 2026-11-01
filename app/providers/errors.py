"""Falhas de provedor. O pipeline converte qualquer `ProviderError` em `needs_review` só na cena
afetada (§2.1, `app.pipeline.failures`); outras exceções são bugs e interrompem a execução."""

from __future__ import annotations

from typing import ClassVar

from app.errors import PipelineError
from app.providers.constants.errors_constants import ErrorsConstants


class ProviderError(PipelineError):
    reason: ClassVar[str] = ErrorsConstants.PROVIDER_ERROR_REASON

    def __init__(self, provider: str, message: str) -> None:
        super().__init__(f"{provider}: {message}")
        self.provider = provider


class QuotaExhausted(ProviderError):
    reason = ErrorsConstants.QUOTA_EXHAUSTED_REASON


class ModelUnavailable(ProviderError):
    """Modelo ausente ou aposentado. Nunca trocar de modelo sozinho (§2.1, §8)."""

    reason = ErrorsConstants.MODEL_UNAVAILABLE_REASON


class LicenseUnknown(ProviderError):
    reason = ErrorsConstants.LICENSE_UNKNOWN_REASON


class InvalidOutput(ProviderError):
    """Resposta fora do schema pedido (ex.: JSON do LLM que não valida)."""

    reason = ErrorsConstants.INVALID_OUTPUT_REASON


class PaidApiBlocked(ProviderError):
    reason = ErrorsConstants.PAID_API_BLOCKED_REASON
