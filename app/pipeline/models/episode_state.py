from __future__ import annotations

from app.pipeline.models._schemas_types import EpisodeId
from app.pipeline.models.model import Model
from app.pipeline.models.status import Status
from app.pipeline.models.step import Step
from app.pipeline.models.step_state import StepState


class EpisodeState(Model):
    episode_id: EpisodeId
    steps: dict[Step, StepState] = {}

    def get(self, step: Step) -> StepState:
        return self.steps.get(step, StepState())

    @property
    def protected_outputs(self) -> set[str]:
        return {
            out for state in self.steps.values() if state.status is Status.APPROVED for out in state.outputs
        }
