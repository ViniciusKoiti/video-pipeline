"""Gates humanos das etapas feitas por agente ou por pessoa (ADR 009): o que cada decisão carimba e se vale.

O `review.json` é a fonte da verdade (§5). Cada decisão guarda o `input_hash` do que foi revisto; se o
conteúdo muda depois, a decisão deixa de valer e `vp status` mostra isso.

- gate 1 (`sources`): `sources.json` + `facts.json`;
- gate 2 (`script`): `scenes.json` + `outline.md`;
- gate 3 (`assets`), por ativo: o arquivo de mídia em `assets/<id>.<ext>`. Aprovar reflete `review_status`
  no `assets/<id>.json`, e o schema recusa sem licença, crédito, `sha256` ou conferência (ADR 007).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from app.pipeline.ports import ManifestStore, ReviewGate
from app.pipeline.schemas import Asset, Decision, ReviewEntry, Status, Step
from app.pipeline.state import Clock, compute_input_hash

GATE_FILES: dict[Step, tuple[str, ...]] = {
    Step.SOURCES: ("sources.json", "facts.json"),
    Step.SCRIPT: ("scenes.json", "outline.md"),
}
GATED_STEPS = (*GATE_FILES, Step.ASSETS)
MEDIA_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm")


class GateError(ValueError):
    pass


@dataclass(frozen=True)
class GateStatus:
    step: Step
    asset_id: str | None
    entry: ReviewEntry | None  # última decisão; None = nenhuma
    current_hash: str | None  # None = o que foi revisto não existe mais

    @property
    def valid(self) -> bool:
        return self.entry is not None and self.entry.input_hash == self.current_hash


def gate_hash(store: ManifestStore, episode_id: str, step: Step, asset_id: str | None = None) -> str:
    """Hash do que o humano revê nesse gate; mesmo conteúdo, mesmo hash."""
    if step is Step.ASSETS:
        if asset_id is None:
            raise GateError("a etapa assets decide ativo por ativo: informe --asset")
        return "sha256:" + _file_sha256(_media_path(store, episode_id, asset_id))
    if asset_id is not None:
        raise GateError("--asset só vale para a etapa assets")
    names = GATE_FILES.get(step)
    if names is None:
        raise GateError(f"a etapa {step.value} ainda não tem gate por comando")
    paths = [store.path(episode_id, name) for name in names]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise GateError(f"{episode_id}: faltam {', '.join(missing)} para o gate de {step.value}")
    return compute_input_hash(paths, {}, base=store.path(episode_id, ""))


def record_decision(
    store: ManifestStore,
    review: ReviewGate,
    episode_id: str,
    step: Step,
    decision: Decision,
    *,
    reviewer: str,
    now: Clock,
    asset_id: str | None = None,
    notes: str = "",
) -> ReviewEntry:
    """Grava a decisão humana no review.json; aprovar um ativo também reflete `review_status` no JSON dele."""
    with store.lock(episode_id):
        input_hash = gate_hash(store, episode_id, step, asset_id)
        approved_asset = None
        if asset_id is not None and decision is Decision.APPROVED:
            approved_asset = _approved(store, episode_id, asset_id, input_hash)
        entry = ReviewEntry(
            step=step,
            asset_id=asset_id,
            decision=decision,
            reviewer=reviewer,
            at=now(),
            input_hash=input_hash,
            notes=notes,
        )
        review.record(episode_id, entry)
        if approved_asset is not None:
            store.write(episode_id, f"assets/{asset_id}.json", approved_asset)
        return entry


def gate_report(store: ManifestStore, review: ReviewGate, episode_id: str) -> list[GateStatus]:
    """Última decisão de cada gate e de cada ativo (os que existem e os que só estão no review.json)."""
    log = review.log(episode_id)
    targets: list[tuple[Step, str | None]] = [(step, None) for step in GATE_FILES]
    on_disk = {p.stem for p in store.path(episode_id, "assets").glob("*.json")}
    decided = {e.asset_id for e in log.entries if e.step is Step.ASSETS and e.asset_id}
    targets += [(Step.ASSETS, asset_id) for asset_id in sorted(on_disk | decided)]
    return [
        GateStatus(step, asset, log.latest(step, asset_id=asset), _current(store, episode_id, step, asset))
        for step, asset in targets
    ]


def _approved(store: ManifestStore, episode_id: str, asset_id: str, input_hash: str) -> Asset:
    asset = store.read(episode_id, f"assets/{asset_id}.json", Asset)
    if asset.review_status is Status.APPROVED:
        raise GateError(f"{asset_id} já está aprovado")
    if asset.sha256 is None or f"sha256:{asset.sha256}" != input_hash:
        raise GateError(f"{asset_id}: o arquivo de mídia não bate com o sha256 do JSON (baixado de novo?)")
    try:
        return Asset.model_validate({**asset.model_dump(), "review_status": Status.APPROVED})
    except ValidationError as error:
        problems = "; ".join(e["msg"].removeprefix("Value error, ") for e in error.errors())
        raise GateError(f"{asset_id}: {problems}") from None


def _current(store: ManifestStore, episode_id: str, step: Step, asset_id: str | None = None) -> str | None:
    try:
        return gate_hash(store, episode_id, step, asset_id)
    except GateError:
        return None


def _media_path(store: ManifestStore, episode_id: str, asset_id: str) -> Path:
    for suffix in MEDIA_SUFFIXES:
        path = store.path(episode_id, f"assets/{asset_id}{suffix}")
        if path.is_file():
            return path
    raise GateError(f"{asset_id}: nenhum arquivo de mídia em assets/")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()
