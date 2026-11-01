"""Etapa por cena com retomada (RF2, §5): cada cena deixa um registro no `manifest.json`.

Uma rodada tenta só as cenas que faltam: nunca tentadas, falhas recuperáveis (`ProviderError`), bloqueadas
por outra cena ou com a saída ausente ou vazia no disco. Cena concluída e íntegra não é refeita. O estado
vem do disco, então o processo pode morrer e voltar. Uma cena só vira `COMPLETED` depois que a ação
terminou e as saídas existem; interromper no meio deixa a cena sem registro, nunca "concluída".

A etapa fica `needs_review` quando falta cena (produção incompleta, `pending_scenes`) ou quando ela tem gate
humano (`needs_review=True`); só o primeiro caso volta a rodar com a mesma entrada. Erro que não é de
provedor é bug: a etapa vira `failed`, as cenas já concluídas ficam gravadas e a exceção sobe.

Uma execução por vez, com um único lock: não aninhar `store.lock` dentro da ação.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime

from app.pipeline.models.action import Action
from app.pipeline.models.episode_state import EpisodeState
from app.pipeline.models.scene_outcome import SceneOutcome
from app.pipeline.models.scene_record import SceneRecord
from app.pipeline.models.scene_run import SceneRun
from app.pipeline.models.step_state import StepState
from app.pipeline.ports import ManifestStore
from app.pipeline.schemas import Status, Step
from app.pipeline.state import (
    Clock,
    InputChanged,
    InputHash,
    OutputMissing,
    StaleApproval,
    load_state,
    output_is_intact,
    save_step,
    transition,
)
from app.providers.errors import ProviderError

SceneAction = Callable[[str], list[str]]  # produz a cena e devolve as saídas, relativas ao episódio


def run_scenes(
    store: ManifestStore,
    episode_id: str,
    step: Step,
    input_hash: InputHash,
    scene_ids: Sequence[str],
    action: SceneAction,
    *,
    now: Clock,
    needs_review: bool = False,
    depends_on: Mapping[str, Sequence[str]] | None = None,
) -> SceneRun:
    with store.lock(episode_id):
        digest = input_hash() if callable(input_hash) else input_hash
        state = load_state(store, episode_id)
        current = state.get(step)
        fresh = current.input_hash == digest
        records = {k: v for k, v in current.scenes.items() if fresh and k in scene_ids}
        todo = [s for s in scene_ids if not _intact(store, episode_id, records.get(s))]
        done_already = fresh and not todo and current.status in (Status.COMPLETED, Status.NEEDS_REVIEW)
        if _guard_approved(current, fresh, todo) or done_already:
            return SceneRun(Action.REUSE, current, _outcomes(current, scene_ids))
        running = transition(
            current, Status.RUNNING, input_hash=digest, scenes=records, outputs=[],
            started_at=now(), finished_at=None, error="",
        )
        state = save_step(store, state, step, running)
        try:
            for scene_id in todo:
                records[scene_id] = _attempt(store, episode_id, scene_id, action, records, depends_on or {})
                state = save_step(store, state, step, running.model_copy(update={"scenes": dict(records)}))
            if callable(input_hash) and input_hash() != digest:
                raise InputChanged(f"{episode_id}: a entrada de {step.value} mudou durante a execução")
        except Exception as error:
            _record_failure(store, state, step, running, records, error, now())
            raise
        done = _finish(running, records, scene_ids, needs_review, now())
        save_step(store, state, step, done)
        return SceneRun(Action.RUN, done, _outcomes(done, scene_ids))


def _record_failure(
    store: ManifestStore, state: EpisodeState, step: Step, running: StepState,
    records: Mapping[str, SceneRecord], error: Exception, at: datetime,
) -> None:
    """Erro inesperado: a etapa vira `failed`, com as cenas já concluídas gravadas; quem chama relança."""
    reason = error.reason if isinstance(error, ProviderError) else "erro_inesperado"
    message = f"{reason}: {error}"[:500]
    failed = transition(running, Status.FAILED, scenes=dict(records), error=message, finished_at=at)
    save_step(store, state, step, failed)


def _guard_approved(current: StepState, fresh: bool, todo: Sequence[str]) -> bool:
    """Etapa aprovada nunca roda sozinha (§2.6): reaproveita, ou recusa com o motivo."""
    if current.status is not Status.APPROVED:
        return False
    if not fresh:
        raise StaleApproval("etapa aprovada com entrada diferente: reabra com `vp reopen` (§2.6)")
    if todo:
        raise OutputMissing(f"etapa aprovada sem saída íntegra de {', '.join(todo)}: reabra com `vp reopen`")
    return True


def _intact(store: ManifestStore, episode_id: str, record: SceneRecord | None) -> bool:
    return (
        record is not None
        and record.status is Status.COMPLETED
        and all(output_is_intact(store.path(episode_id, name)) for name in record.outputs)
    )


def _attempt(
    store: ManifestStore,
    episode_id: str,
    scene_id: str,
    action: SceneAction,
    records: Mapping[str, SceneRecord],
    depends_on: Mapping[str, Sequence[str]],
) -> SceneRecord:
    blocked = [d for d in depends_on.get(scene_id, ()) if not _intact(store, episode_id, records.get(d))]
    if blocked:
        return SceneRecord(status=Status.PENDING, reason="blocked", detail=f"depende de {', '.join(blocked)}")
    try:
        outputs = action(scene_id)
    except ProviderError as error:
        return SceneRecord(status=Status.NEEDS_REVIEW, reason=error.reason, detail=str(error))
    finished = SceneRecord(status=Status.COMPLETED, outputs=outputs)
    if not outputs or not _intact(store, episode_id, finished):
        raise OutputMissing(f"{episode_id}/{scene_id}: a ação terminou sem a saída {outputs or '(nenhuma)'}")
    return finished


def _finish(
    running: StepState, records: Mapping[str, SceneRecord], scene_ids: Sequence[str], needs_review: bool,
    at: datetime,
) -> StepState:
    incomplete = any(records[s].status is not Status.COMPLETED for s in scene_ids)
    final = Status.NEEDS_REVIEW if incomplete or needs_review else Status.COMPLETED
    outputs = [name for s in scene_ids if s in records for name in records[s].outputs]
    return transition(running, final, scenes=dict(records), outputs=outputs, finished_at=at)


def _outcomes(state: StepState, scene_ids: Sequence[str]) -> list[SceneOutcome[list[str]]]:
    """O desfecho de cada cena, lido do estado gravado (vale também quando nada rodou agora)."""
    outcomes: list[SceneOutcome[list[str]]] = []
    for scene_id in scene_ids:
        record = state.scenes.get(scene_id, SceneRecord())
        value = record.outputs if record.status is Status.COMPLETED else None
        outcomes.append(SceneOutcome(scene_id, record.status, value, record.reason, record.detail))
    return outcomes
