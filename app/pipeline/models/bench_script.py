from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.pipeline.models.bench_claim import BenchClaim


class BenchScript(BaseModel):
    model_config = ConfigDict(extra="forbid")

    narration: str = Field(min_length=1)
    claims: list[BenchClaim] = Field(min_length=1)
