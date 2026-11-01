from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import (
    AliasChoices,
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.pipeline.models._usage_types import TOKEN_FIELDS, Count, Identifier


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
