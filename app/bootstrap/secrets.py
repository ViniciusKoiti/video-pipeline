"""Segredos do `.env` para as fábricas da composição (§2.7): ausente é `ConfigurationError`, e o valor nunca
aparece na mensagem."""

from __future__ import annotations

from pydantic import SecretStr

from app.bootstrap.registry import ConfigurationError
from app.settings import Settings


def secret(settings: Settings, env_name: str) -> str:
    value = getattr(settings.secrets, env_name.lower())
    if not isinstance(value, SecretStr):
        raise ConfigurationError(f"{env_name} ausente no .env")
    return value.get_secret_value()
