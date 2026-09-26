"""Estados por etapa, cache por `input_hash` e imutabilidade do que foi aprovado (§5, §2.6).

O `manifest.json` de cada episódio guarda o estado de cada etapa. A chave de cache é
`(episode_id, step, input_hash)`: mesma entrada, reaproveita; entrada nova, refaz — exceto etapa aprovada,
que nunca é refeita nem sobrescrita sem reabertura explícita (`reopen_step`, registrada no review.json).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import AwareDatetime, BaseModel

from app.pipeline.ports import ImmutableManifest, ManifestNotFound, ManifestStore, ReviewGate
from app.pipeline.schemas import Decision, EpisodeId, Model, RelPath, ReviewEntry, Status, Step
from app.providers.errors import ProviderError

MANIFEST = "manifest.json"
Clock = Callable[[], datetime]


class StepState(Model):
    status: Status = Status.PENDING
    input_hash: str | None = None
    outputs: list[RelPath] = []  # arquivos gerados, relativos à pasta do episódio
    started_at: AwareDatetime | None = None
    finished_at: AwareDatetime | None = None
    error: str = ""  # motivo da última falha (ex.: "quota_exhausted: ...")


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


# Transições do §5. Sair de APPROVED/COMPLETED para refazer só por reabertura explícita (reopen_step).
TRANSITIONS: dict[Status, frozenset[Status]] = {
    Status.PENDING: frozenset({Status.RUNNING}),
    Status.RUNNING: frozenset({Status.NEEDS_REVIEW, Status.COMPLETED, Status.FAILED}),
    Status.NEEDS_REVIEW: frozenset(
        {Status.APPROVED, Status.RUNNING}
    ),  # aprovação, ou refazer com entrada nova
    Status.APPROVED: frozenset({Status.COMPLETED}),
    Status.COMPLETED: frozenset({Status.RUNNING}),  # etapa sem gate humano com entrada nova
    Status.FAILED: frozenset({Status.RUNNING}),
}


class InvalidTransition(ValueError):
    pass


class StaleApproval(RuntimeError):
    """Etapa aprovada recebeu entrada diferente: refazer exige reabrir (§2.6)."""


class Action(StrEnum):
    RUN = "run"
    REUSE = "reuse"


def transition(state: StepState, to: Status, **changes: object) -> StepState:
    if to not in TRANSITIONS[state.status]:
        raise InvalidTransition(f"{state.status} → {to} não é permitido (§5)")
    return state.model_copy(update={"status": to, **changes})


def plan(state: StepState, input_hash: str) -> Action:
    """Decide se a etapa roda ou reaproveita o resultado guardado."""
    same_input = state.input_hash == input_hash
    if same_input and state.status in (Status.APPROVED, Status.COMPLETED, Status.NEEDS_REVIEW):
        return Action.REUSE
    if state.status is Status.APPROVED:
        raise StaleApproval(
            "etapa aprovada com entrada diferente: reabra com `vp reopen` antes de refazer (§2.6)"
        )
    return Action.RUN


def compute_input_hash(files: Iterable[Path], params: Mapping[str, object], *, base: Path) -> str:
    """Hash do conteúdo das entradas e dos parâmetros que mudam o resultado (modelo, voz, motor)."""
    digest = hashlib.sha256()
    for path in sorted(files):
        digest.update(path.relative_to(base).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    digest.update(json.dumps(params, sort_keys=True, default=str).encode())
    return "sha256:" + digest.hexdigest()


def load_state(store: ManifestStore, episode_id: str) -> EpisodeState:
    try:
        return store.read(episode_id, MANIFEST, EpisodeState)
    except ManifestNotFound:
        return EpisodeState(episode_id=episode_id)


def _save(store: ManifestStore, state: EpisodeState, step: Step, step_state: StepState) -> EpisodeState:
    updated = state.model_copy(update={"steps": {**state.steps, step: step_state}})
    store.write(state.episode_id, MANIFEST, updated)
    return updated


@dataclass(frozen=True)
class StepResult:
    outputs: list[str]
    needs_review: bool  # True = etapa com gate humano (fica em needs_review até aprovação)


@dataclass(frozen=True)
class StepRun:
    action: Action
    state: StepState


def run_step(
    store: ManifestStore,
    episode_id: str,
    step: Step,
    input_hash: str,
    action: Callable[[], StepResult],
    *,
    now: Clock,
) -> StepRun:
    """Roda a etapa só se preciso, com o episódio travado. Falha fica registrada e a exceção sobe."""
    with store.lock(episode_id):
        state = load_state(store, episode_id)
        current = state.get(step)
        if plan(current, input_hash) is Action.REUSE:
            return StepRun(Action.REUSE, current)
        running = transition(
            current,
            Status.RUNNING,
            input_hash=input_hash,
            outputs=[],
            started_at=now(),
            finished_at=None,
            error="",
        )
        state = _save(store, state, step, running)
        try:
            result = action()
        except Exception as error:
            reason = error.reason if isinstance(error, ProviderError) else "erro_inesperado"
            _save(
                store,
                state,
                step,
                transition(running, Status.FAILED, error=f"{reason}: {error}"[:500], finished_at=now()),
            )
            raise
        final = Status.NEEDS_REVIEW if result.needs_review else Status.COMPLETED
        done = transition(running, final, outputs=result.outputs, finished_at=now())
        _save(store, state, step, done)
        return StepRun(Action.RUN, done)


def write_output(store: ManifestStore, episode_id: str, name: str, manifest: BaseModel) -> None:
    """Escreve um manifesto de saída, recusando os que pertencem a etapa aprovada (§2.6)."""
    if name in load_state(store, episode_id).protected_outputs:
        raise ImmutableManifest(f"{episode_id}/{name} pertence a uma etapa aprovada; reabra antes (§2.6)")
    store.write(episode_id, name, manifest)


def approve_step(
    store: ManifestStore,
    review: ReviewGate,
    episode_id: str,
    step: Step,
    *,
    reviewer: str,
    now: Clock,
    notes: str = "",
) -> StepState:
    """Registra a aprovação humana no review.json (fonte da verdade) e reflete no manifest.json."""
    with store.lock(episode_id):
        state = load_state(store, episode_id)
        approved = transition(state.get(step), Status.APPROVED)
        review.record(
            episode_id,
            ReviewEntry(
                step=step,
                decision=Decision.APPROVED,
                reviewer=reviewer,
                at=now(),
                input_hash=approved.input_hash,
                notes=notes,
            ),
        )
        _save(store, state, step, approved)
        return approved


def reopen_step(
    store: ManifestStore,
    review: ReviewGate,
    episode_id: str,
    step: Step,
    *,
    reviewer: str,
    reason: str,
    now: Clock,
) -> StepState:
    """Única saída de uma etapa aprovada/concluída para refazer: explícita, com motivo no review.json."""
    with store.lock(episode_id):
        state = load_state(store, episode_id)
        current = state.get(step)
        if current.status not in (Status.APPROVED, Status.COMPLETED):
            raise InvalidTransition(f"só etapa aprovada ou concluída é reaberta (está {current.status})")
        review.record(
            episode_id,
            ReviewEntry(
                step=step,
                decision=Decision.CHANGES_REQUESTED,
                reviewer=reviewer,
                at=now(),
                input_hash=current.input_hash,
                notes=f"reaberta: {reason}",
            ),
        )
        reopened = current.model_copy(update={"status": Status.PENDING, "finished_at": None})
        _save(store, state, step, reopened)
        return reopened
