"""O que cada gate carimba (CLAUDE.md §4): o hash do conteúdo que o humano revê, e o erro de gate.

Mora em `governance` (ADR 064): a proteção de escrita e a reabertura comparam o carimbo sem depender de
como a decisão é registrada (`gates.py`), e o hash da tradução fica aqui pelo mesmo motivo. A lista do
que cada gate carimba está no `gates.py`.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from app.errors import PipelineError
from app.pipeline.constants.gates_constants import GatesConstants as Constants
from app.pipeline.constants.translation_constants import TranslationConstants
from app.pipeline.file_hash import sha256_file
from app.pipeline.governance.review_hashes import content_hash, legacy_hashes_of
from app.pipeline.governance.state import compute_input_hash
from app.pipeline.models.translation_link import TranslationLink
from app.pipeline.ports import ManifestNotFound, ManifestStore
from app.pipeline.schemas import Step


class GateError(PipelineError, ValueError):
    """Gate que não pode ser decidido, conferido ou reaberto (arquivo faltando, parecer ausente)."""


def gate_hash(store: ManifestStore, episode_id: str, step: Step, asset_id: str | None = None) -> str:
    """Hash do que o humano revê nesse gate; mesmo conteúdo, mesmo hash."""
    if step is Step.ASSETS:
        if asset_id is None:
            raise GateError("a etapa assets decide ativo por ativo: informe --asset")
        return "sha256:" + sha256_file(_media_path(store, episode_id, asset_id))
    if asset_id is not None:
        raise GateError("--asset só vale para a etapa assets")
    if step is Step.PREVIEW:
        return compute_input_hash(_preview_paths(store, episode_id), {}, base=store.path(episode_id, ""))
    if step is Step.TRANSLATION:
        if not store.path(episode_id, TranslationConstants.LINK_FILE).is_file():
            raise GateError(
                f"{episode_id}: sem {TranslationConstants.LINK_FILE}, não é uma tradução (ADR 034)"
            )
        try:
            return translation_hash(store, episode_id)
        except (ManifestNotFound, ValueError) as error:
            raise GateError(
                f"{episode_id}: {TranslationConstants.LINK_FILE} inválido ou sem o original ({error})"
            ) from None
    names = Constants.GATE_FILES.get(step)
    if names is None:
        raise GateError(f"a etapa {step.value} ainda não tem gate por comando")
    paths = [store.path(episode_id, name) for name in names]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise GateError(f"{episode_id}: faltam {', '.join(missing)} para o gate de {step.value}")
    return content_hash(paths, base=store.path(episode_id, ""))


def current_hash(store: ManifestStore, episode_id: str, step: Step, asset: str | None = None) -> str | None:
    try:
        return gate_hash(store, episode_id, step, asset)
    except GateError:
        return None


def legacy_hashes(store: ManifestStore, episode_id: str, step: Step) -> tuple[str, ...]:
    """Os carimbos das regras anteriores (arquivo inteiro e asset_id como null): decisões antigas valem."""
    names = Constants.GATE_FILES.get(step)
    paths = [store.path(episode_id, name) for name in names or ()]
    if not paths or not all(p.is_file() for p in paths):
        return ()
    return legacy_hashes_of(paths, base=store.path(episode_id, ""))


def translation_hash(store: ManifestStore, episode_id: str) -> str:
    """O que o gate de tradução carimba: a tradução, o vínculo e o original de que ela vem.

    Mudar a narração (ou a tela) do original derruba a aprovação da tradução (§5)."""
    link = store.read(episode_id, TranslationConstants.LINK_FILE, TranslationLink)
    narration, content = TranslationConstants.NARRATION_FILE, TranslationConstants.CONTENT_FILE
    own = (narration, TranslationConstants.LINK_FILE, content)
    origin = (narration, content)
    labelled = [(f"{episode_id}/{n}", store.path(episode_id, n)) for n in own]
    labelled += [(f"{link.derived_from}/{n}", store.path(link.derived_from, n)) for n in origin]
    digest = hashlib.sha256()
    for label, path in labelled:
        if path.is_file():
            digest.update(label.encode() + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return "sha256:" + digest.hexdigest()


def _preview_paths(store: ManifestStore, episode_id: str) -> list[Path]:
    render = next(
        (store.path(episode_id, r) for r in Constants.RENDERS if store.path(episode_id, r).is_file()), None
    )
    if render is None:
        raise GateError(f"{episode_id}: nenhum render em renders/ para o gate da prévia")
    extras = [store.path(episode_id, name) for name in Constants.PREVIEW_FILES]
    return [render, *(p for p in extras if p.is_file())]


def _media_path(store: ManifestStore, episode_id: str, asset_id: str) -> Path:
    for suffix in Constants.MEDIA_SUFFIXES:
        path = store.path(episode_id, f"assets/{asset_id}{suffix}")
        if path.is_file():
            return path
    raise GateError(f"{asset_id}: nenhum arquivo de mídia em assets/")
