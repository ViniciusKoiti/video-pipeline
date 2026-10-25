"""Contratos do registro de consumo editorial; valores monetários são estimativas (ADR 032)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Protocol

from pydantic import (
    AliasChoices,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

Identifier = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=512)
]
Count = Annotated[int, Field(strict=True, ge=0, le=2**63 - 1)]
Metric = Literal["tokens_total", "cost_usd_micros"]
TOKEN_FIELDS = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens")


class UsageError(ValueError):
    """Conflito de identidade, orçamento ou conciliação que exige corrigir a entrada."""


class AgentRun(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: Identifier
    project: Identifier = "auto-play"
    episode_id: Identifier
    stage: Identifier
    agent_name: Identifier
    parent_run_id: Identifier | None = None
    session_id: Identifier | None = None


class UsageBudget(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: Identifier
    project: Identifier = "auto-play"
    episode_id: Identifier
    model_filter: Identifier = "*"
    metric: Metric
    limit_value: Count


class UsageRequest(BaseModel):
    # Só campos permitidos são persistidos, mesmo se a exportação incluir texto privado.
    model_config = ConfigDict(extra="ignore", frozen=True)

    event_key: Identifier = Field(validation_alias=AliasChoices("event_key", "request_id"))
    provider_request_id: Identifier | None = Field(
        default=None, validation_alias=AliasChoices("provider_request_id", "request_id")
    )
    model: Identifier
    occurred_at: AwareDatetime = Field(validation_alias=AliasChoices("occurred_at", "event.timestamp"))
    input_tokens: Count | None = None
    output_tokens: Count | None = None
    cache_read_tokens: Count | None = None
    cache_write_tokens: Count | None = Field(
        default=None, validation_alias=AliasChoices("cache_write_tokens", "cache_creation_tokens")
    )
    cost_usd_micros: Count | None = None
    duration_ms: Count | None = None
    status: Literal["success", "error"] = "success"

    @field_validator("occurred_at")
    @classmethod
    def utc(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def token_range(self) -> UsageRequest:
        if sum(getattr(self, name) or 0 for name in TOKEN_FIELDS) > 2**63 - 1:
            raise ValueError("soma de tokens excede o intervalo do SQLite")
        return self


class UsageLedger(Protocol):
    """Porta de telemetria; não executa modelos nem aprova decisões editoriais."""

    @property
    def path(self) -> Path: ...

    def create_run(self, run: AgentRun) -> None: ...
    def set_budget(self, budget: UsageBudget) -> None: ...
    def reserve(self, run_id: str, allocations: Mapping[str, int]) -> None: ...
    def record(self, run_id: str, requests: Sequence[UsageRequest]) -> dict[str, int]: ...
    def finish(self, run_id: str, *, reconciled: bool = False) -> str: ...
    def report(self, project: str, episode_id: str) -> dict[str, Any]: ...
