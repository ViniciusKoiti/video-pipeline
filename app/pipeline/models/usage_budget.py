from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.pipeline.models._usage_types import Count, Identifier, Metric


class UsageBudget(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: Identifier
    project: Identifier = "auto-play"
    episode_id: Identifier
    model_filter: Identifier = "*"
    metric: Metric
    limit_value: Count
