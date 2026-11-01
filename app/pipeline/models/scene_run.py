from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models.action import Action
from app.pipeline.models.scene_outcome import SceneOutcome
from app.pipeline.models.step_state import StepState


@dataclass(frozen=True)
class SceneRun:
    """Resultado de `run_scenes`: o que foi feito agora (`RUN`) ou só lido do disco (`REUSE`), mais o
    desfecho de cada cena na ordem pedida, sempre reconstruído do estado gravado."""

    action: Action
    state: StepState
    outcomes: list[SceneOutcome[list[str]]]
