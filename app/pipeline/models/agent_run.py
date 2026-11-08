from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.pipeline.models._usage_types import Identifier


class AgentRun(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: Identifier
    project: Identifier = "auto-play"
    episode_id: Identifier
    stage: Identifier
    agent_name: Identifier
    parent_run_id: Identifier | None = None
    session_id: Identifier | None = None
