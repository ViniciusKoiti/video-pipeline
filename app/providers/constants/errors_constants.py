"""Códigos estáveis das falhas de provedores."""

from typing import Final


class ErrorsConstants:
    PROVIDER_ERROR_REASON: Final[str] = 'provider_error'
    QUOTA_EXHAUSTED_REASON: Final[str] = 'quota_exhausted'
    MODEL_UNAVAILABLE_REASON: Final[str] = 'model_unavailable'
    LICENSE_UNKNOWN_REASON: Final[str] = 'license_unknown'
    INVALID_OUTPUT_REASON: Final[str] = 'invalid_output'
    PAID_API_BLOCKED_REASON: Final[str] = 'paid_api_blocked'
