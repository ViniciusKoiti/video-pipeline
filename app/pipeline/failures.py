"""Falha de provedor para a cena, não o episódio (§2.1, §5)."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Generic, TypeVar

from app.pipeline.schemas import Status
from app.providers.errors import ProviderError

R = TypeVar("R")


@dataclass(frozen=True)
class SceneOutcome(Generic[R]):
    scene_id: str
    status: Status  # COMPLETED ou NEEDS_REVIEW
    value: R | None = None
    reason: str = ""  # ProviderError.reason, para registrar em review.json
    detail: str = ""


def for_each_scene(scene_ids: Iterable[str], action: Callable[[str], R]) -> list[SceneOutcome[R]]:
    """Roda `action` em cada cena. `ProviderError` vira needs_review só naquela cena;
    qualquer outra exceção é bug e interrompe a execução."""
    outcomes: list[SceneOutcome[R]] = []
    for scene_id in scene_ids:
        try:
            outcomes.append(SceneOutcome(scene_id, Status.COMPLETED, value=action(scene_id)))
        except ProviderError as error:
            outcome = SceneOutcome[R](scene_id, Status.NEEDS_REVIEW, reason=error.reason, detail=str(error))
            outcomes.append(outcome)
    return outcomes
