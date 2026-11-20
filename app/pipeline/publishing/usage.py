"""Contratos do registro de consumo editorial; valores monetários são estimativas (ADR 032)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol

from app.errors import PipelineError
from app.pipeline.models._usage_types import Count as Count
from app.pipeline.models._usage_types import Identifier as Identifier
from app.pipeline.models._usage_types import Metric as Metric
from app.pipeline.models.agent_run import AgentRun as AgentRun
from app.pipeline.models.usage_budget import UsageBudget as UsageBudget
from app.pipeline.models.usage_request import UsageRequest as UsageRequest


class UsageError(PipelineError, ValueError):
    """Conflito de identidade, orçamento ou conciliação que exige corrigir a entrada."""


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
