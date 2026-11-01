"""Contratos do registro de provedores; nenhuma implementação concreta entra aqui."""

from __future__ import annotations

from collections.abc import Mapping

from app.bootstrap.models._bootstrap_registry_types import Factory as Factory
from app.bootstrap.models._bootstrap_registry_types import T_co as T_co
from app.bootstrap.models.registration import Registration as Registration
from app.bootstrap.models.registry import Registry as Registry
from app.errors import PipelineError
from app.providers.base import ProviderInfo
from app.providers.errors import PaidApiBlocked
from app.settings import Budget, Settings


class ConfigurationError(PipelineError, ValueError):
    pass


def ensure_free(info: ProviderInfo, budget: Budget) -> None:
    """§2.1: custo > 0 só com ALLOW_PAID_API=true e teto de gasto > 0."""
    if info.usd_per_call > 0 and not (budget.allow_paid_api and budget.max_api_spend_usd > 0):
        raise PaidApiBlocked(
            info.name, f"custa US$ {info.usd_per_call} por chamada e ALLOW_PAID_API=false (§2.1)"
        )


def _choices(settings: Settings) -> dict[str, list[str]]:
    chosen = settings.providers.model_dump()
    flat: dict[str, list[str]] = {}
    for port, names in chosen.items():
        if names is None:
            continue
        if isinstance(names, dict):  # render: formato -> motor
            names = list(names.values())
        port = "tts" if port == "tts_final" else port  # a voz final vem da mesma porta
        flat.setdefault(port, [])
        flat[port] += names if isinstance(names, list) else [names]
    return flat


def unknown_choices(settings: Settings, registry: Registry) -> list[str]:
    problems = []
    for port, names in _choices(settings).items():
        options = registry.get(port, {})
        assert isinstance(options, Mapping)
        problems += [
            f"{port} = {name!r} não existe (opções: {', '.join(sorted(options)) or 'nenhuma'})"
            for name in names
            if name not in options
        ]
    return problems
