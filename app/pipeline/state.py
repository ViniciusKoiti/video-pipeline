"""Estados por etapa, cache por `input_hash` e imutabilidade do que foi aprovado (§5, §2.6).

O `manifest.json` de cada episódio guarda o estado de cada etapa. A chave de cache é
`(episode_id, step, input_hash)`: mesma entrada, reaproveita; entrada nova, refaz — exceto etapa aprovada,
que nunca é refeita nem sobrescrita sem reabertura explícita (`reopen_step`, registrada no review.json).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from app.pipeline.constants.state_constants import StateConstants
from app.pipeline.models.action import Action as Action
from app.pipeline.models.episode_state import EpisodeState as EpisodeState
from app.pipeline.models.step_result import StepResult as StepResult
from app.pipeline.models.step_run import StepRun as StepRun
from app.pipeline.models.step_state import StepState as StepState
from app.pipeline.ports import ImmutableManifest, ManifestNotFound, ManifestStore, ReviewGate, WriteGuard
from app.pipeline.schemas import Decision, ReviewEntry, Status, Step
from app.providers.errors import ProviderError

Clock = Callable[[], datetime]
InputHash = str | Callable[[], str]  # um callable é resolvido sob o lock e conferido de novo no fim


# Transições do §5. Sair de APPROVED/COMPLETED para refazer só por reabertura explícita (reopen_step).


class InvalidTransition(ValueError):
    pass


class StaleApproval(RuntimeError):
    """Etapa aprovada recebeu entrada diferente: refazer exige reabrir (§2.6)."""


class OutputMissing(RuntimeError):
    """Etapa aprovada com saída ausente ou inválida: o código não a recria; reabra para refazer (§2.6)."""


class InputChanged(RuntimeError):
    """A entrada mudou durante a execução: o resultado não vale e nada é marcado como concluído."""


def transition(state: StepState, to: Status, **changes: object) -> StepState:
    if to not in StateConstants.TRANSITIONS[state.status]:
        raise InvalidTransition(f"{state.status} → {to} não é permitido (§5)")
    return state.model_copy(update={"status": to, **changes})


def plan(state: StepState, input_hash: str, *, missing: Sequence[str] = ()) -> Action:
    """Decide se a etapa roda ou reaproveita o resultado guardado.

    Só se reaproveita resultado íntegro: cena tentada e não concluída (`pending_scenes`) ou saída ausente
    (`missing`) pedem nova rodada; revisão humana pendente (`needs_review` sem cena pendente) não.
    Etapa aprovada nunca roda sozinha: entrada nova ou saída ausente exigem reabrir (§2.6)."""
    same_input = state.input_hash == input_hash
    if state.status is Status.APPROVED:
        if not same_input:
            raise StaleApproval(
                "etapa aprovada com entrada diferente: reabra com `vp reopen` antes de refazer (§2.6)"
            )
        if missing:
            raise OutputMissing(f"etapa aprovada sem a saída {', '.join(missing)}: reabra com `vp reopen`")
        return Action.REUSE
    done = state.status in (Status.COMPLETED, Status.NEEDS_REVIEW)
    return Action.REUSE if same_input and done and not state.pending_scenes and not missing else Action.RUN


def missing_outputs(store: ManifestStore, episode_id: str, state: StepState) -> list[str]:
    """Saídas registradas que não existem mais (ou estão vazias) na pasta do episódio."""
    return [name for name in state.outputs if not output_is_intact(store.path(episode_id, name))]


def output_is_intact(path: Path) -> bool:
    return path.exists() and (not path.is_file() or path.stat().st_size > 0)


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
        return store.read(episode_id, StateConstants.MANIFEST, EpisodeState)
    except ManifestNotFound:
        return EpisodeState(episode_id=episode_id)


def save_step(store: ManifestStore, state: EpisodeState, step: Step, step_state: StepState) -> EpisodeState:
    updated = state.model_copy(update={"steps": {**state.steps, step: step_state}})
    store.write(state.episode_id, StateConstants.MANIFEST, updated)
    return updated


def run_step(
    store: ManifestStore,
    episode_id: str,
    step: Step,
    input_hash: InputHash,
    action: Callable[[], StepResult],
    *,
    now: Clock,
) -> StepRun:
    """Roda a etapa só se preciso, com o episódio travado. Falha fica registrada e a exceção sobe.

    Não aninhar `store.lock` dentro da ação: o lock do episódio já é o de `run_step`."""
    with store.lock(episode_id):
        digest = input_hash() if callable(input_hash) else input_hash
        state = load_state(store, episode_id)
        current = state.get(step)
        if plan(current, digest, missing=missing_outputs(store, episode_id, current)) is Action.REUSE:
            return StepRun(Action.REUSE, current)
        running = transition(
            current,
            Status.RUNNING,
            input_hash=digest,
            outputs=[],
            scenes={},
            started_at=now(),
            finished_at=None,
            error="",
        )
        state = save_step(store, state, step, running)
        try:
            result = action()
            if callable(input_hash) and input_hash() != digest:
                raise InputChanged(f"{episode_id}: a entrada de {step.value} mudou durante a execução")
        except Exception as error:
            reason = error.reason if isinstance(error, ProviderError) else "erro_inesperado"
            failed = transition(running, Status.FAILED, error=f"{reason}: {error}"[:500], finished_at=now())
            save_step(store, state, step, failed)
            raise
        final = Status.NEEDS_REVIEW if result.needs_review else Status.COMPLETED
        done = transition(running, final, outputs=result.outputs, finished_at=now())
        save_step(store, state, step, done)
        return StepRun(Action.RUN, done)


def write_output(
    store: ManifestStore, episode_id: str, name: str, manifest: BaseModel, *, guard: WriteGuard
) -> None:
    """Escreve um manifesto de saída, recusando o que uma aprovação protege (§2.6): a etapa aprovada no
    manifest.json ou o que um gate carimbou no review.json (`guard`). Quem chama já segura o lock."""
    if name in load_state(store, episode_id).protected_outputs:
        raise ImmutableManifest(f"{episode_id}/{name} pertence a uma etapa aprovada; reabra antes (§2.6)")
    guard.check(episode_id, name, (manifest.model_dump_json(indent=2) + "\n").encode())
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
        save_step(store, state, step, approved)
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
        save_step(store, state, step, reopened)
        return reopened
