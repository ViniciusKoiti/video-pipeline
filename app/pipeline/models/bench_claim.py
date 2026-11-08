from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BenchClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    excerpt_ids: list[str] = Field(min_length=1)
