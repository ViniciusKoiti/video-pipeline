from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models.action import Action
from app.pipeline.models.step_state import StepState


@dataclass(frozen=True)
class StepRun:
    action: Action
    state: StepState
