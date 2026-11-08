"""Reabertura de gate aprovado: a única saída para refazer o que o humano carimbou (§2.6, §5).

Acrescenta ao `review.json` uma decisão "mudanças pedidas" com motivo e autor, sem apagar nem editar as
anteriores; a decisão mais recente deixa de ser "aprovado" e a proteção do alvo (e só dele) cai. Reabrir um
ativo também devolve o `review_status` do JSON dele a `needs_review`, o que a aprovação tinha refletido.
"""

from __future__ import annotations

from pathlib import Path

from app.pipeline.constants.gates_constants import GatesConstants as Constants
from app.pipeline.gates import GateError
from app.pipeline.ports import ManifestStore, ReviewGate
from app.pipeline.schemas import Asset, Decision, ReviewEntry, Status, Step
from app.pipeline.state import Clock


def reopen_gate(
    store: ManifestStore,
    review: ReviewGate,
    episode_id: str,
    step: Step,
    *,
    reviewer: str,
    reason: str,
    now: Clock,
    asset_id: str | None = None,
) -> ReviewEntry:
    if not reason.strip():
        raise GateError("reabrir pede o motivo (--reason)")
    if step not in Constants.GATED_STEPS:
        raise GateError(f"a etapa {step.value} não tem gate por comando, não há o que reabrir")
    if (step is Step.ASSETS) != (asset_id is not None):
        raise GateError("a etapa assets reabre ativo por ativo (--asset); nas outras, --asset não vale")
    with store.lock(episode_id):
        target = asset_id or step.value
        approved = review.log(episode_id).latest(step, asset_id=asset_id)
        if approved is None or approved.decision is not Decision.APPROVED:
            raise GateError(f"{episode_id}: {target} não está aprovado, nada a reabrir")
        entry = ReviewEntry(
            step=step,
            asset_id=asset_id,
            decision=Decision.CHANGES_REQUESTED,
            reviewer=reviewer,
            at=now(),
            input_hash=approved.input_hash,
            notes=f"reaberta: {reason.strip()}",
        )
        review.record(episode_id, entry)
        if asset_id is not None:
            _release_asset(store, episode_id, asset_id)
        return entry


def _release_asset(store: ManifestStore, episode_id: str, asset_id: str) -> None:
    name = f"assets/{asset_id}.json"
    if not store.exists(episode_id, name):
        return
    asset = store.read(episode_id, name, Asset)
    if asset.review_status is not Status.APPROVED:
        return
    reopened = asset.model_copy(update={"review_status": Status.NEEDS_REVIEW})
    path: Path = store.path(episode_id, name)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(reopened.model_dump_json(indent=2) + "\n")
    tmp.replace(path)  # exceção explícita ao §2.6: é a própria reabertura
