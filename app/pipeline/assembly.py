"""Montagem e render de um episódio (RF6, ADR 051): o que `montar_episodio.py` fazia no fim do `main`.

**O motor vem da porta**, por formato do episódio (`renderers(format)`, o `Context.renderer` da composição):
trocar o motor é trocar uma linha do `providers.toml`, e os testes usam um renderer falso.

**As pré-condições são da operação**, conferidas sob o lock do episódio e antes de qualquer escrita:

- toda cena do `episode.json` tem o WAV, íntegro; todo ativo usado tem o arquivo de mídia em `assets/`;
- o **render final** pede ainda todos os ativos (planos e trilha) aprovados no gate 3 (`review_status`);
  a **prévia** é rascunho e não pede. Montagem incompleta não chega ao motor (`AssemblyError`);
- o `episode.json` e o MP4 de saída passam pelo `WriteGuard` (ADR 039) antes da primeira escrita. Prévia
  (`renders/preview.mp4`) e final (`renders/final.mp4`) são arquivos distintos: o gate 4 aprovado para um
  recusa o render por cima dele, e renderizar o outro é permitido (a aprovação passa a pedir nova decisão,
  #120). O mesmo `episode.json` não é regravado; o novo é gravado inteiro (`write_atomic`).
"""

from __future__ import annotations

from collections.abc import Callable

from app.errors import PipelineError
from app.media.wav import wav_is_valid
from app.pipeline.atomic_files import write_atomic
from app.pipeline.constants.assembly_constants import AssemblyConstants as Constants
from app.pipeline.constants.gates_constants import GatesConstants
from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.ports import ManifestInvalid, ManifestNotFound, ManifestStore, WriteGuard
from app.pipeline.schemas import Asset, EpisodeFormat, EpisodeManifest, ScenesManifest, effective_shots
from app.render.base import RenderEngine, RenderResult


class AssemblyError(PipelineError, ValueError):
    """Montagem incompleta: a mensagem lista o que falta. Nada foi escrito e o motor não foi chamado."""


def asset_ids(scenes: ScenesManifest, episode: EpisodeManifest) -> list[str]:
    """Os ativos que o vídeo usa: os dos planos (também a forma v1 de uma cena) e os da trilha."""
    ids: set[str] = {track.asset_id for track in episode.music}
    for scene in scenes.scenes:
        for shot in effective_shots(scene):
            found = getattr(shot, "asset_id", None)  # só os planos de mídia (foto, b-roll, citação) o têm
            if found:
                ids.add(found)
    return sorted(ids)


def assembly_problems(
    store: ManifestStore,
    episode_id: str,
    scenes: ScenesManifest,
    episode: EpisodeManifest,
    *,
    final: bool,
) -> list[str]:
    problems = [
        f"{scene.id}: falta o WAV {scene.audio} (ou ele não é um WAV válido)"
        for scene in episode.scenes
        if not wav_is_valid(store.path(episode_id, scene.audio))
    ]
    for asset_id in asset_ids(scenes, episode):
        files = (store.path(episode_id, f"assets/{asset_id}{s}") for s in GatesConstants.MEDIA_SUFFIXES)
        if not any(path.is_file() for path in files):
            problems.append(f"ativo {asset_id}: sem arquivo de mídia em assets/")
        if final and not _approved(store, episode_id, asset_id):
            problems.append(f"ativo {asset_id}: não aprovado no gate 3 (o render final exige)")
    return problems


def _approved(store: ManifestStore, episode_id: str, asset_id: str) -> bool:
    try:
        asset = store.read(episode_id, f"assets/{asset_id}.json", Asset)
    except (ManifestNotFound, ManifestInvalid):
        return False
    return asset.review_status in SchemasConstants.APPROVED_STATES


class EpisodeRenderer:
    def __init__(
        self, store: ManifestStore, guard: WriteGuard, renderers: Callable[[EpisodeFormat], RenderEngine]
    ) -> None:
        self._store, self._guard, self._renderers = store, guard, renderers

    def assemble(
        self, episode_id: str, scenes: ScenesManifest, episode: EpisodeManifest, *, final: bool = False
    ) -> bool:
        """Confere a montagem e grava o `episode.json`; devolve se ele mudou. Não renderiza."""
        with self._store.lock(episode_id):
            self._check(episode_id, scenes, episode, final=final)
            return self._write_episode(episode_id, episode)

    def render(
        self, episode_id: str, scenes: ScenesManifest, episode: EpisodeManifest, *, preview: bool
    ) -> RenderResult:
        out_name = Constants.PREVIEW if preview else Constants.FINAL
        with self._store.lock(episode_id):
            self._check(episode_id, scenes, episode, final=not preview)
            engine = self._renderers(episode.format)  # formato sem motor: erro de configuração, nada escrito
            self._guard.check(episode_id, out_name)  # o gate 4 aprovado para este MP4 recusa o render
            self._write_episode(episode_id, episode)
            out = self._store.path(episode_id, out_name)
            return engine.render(episode, self._store.path(episode_id, ""), out, preview=preview)

    def _check(
        self, episode_id: str, scenes: ScenesManifest, episode: EpisodeManifest, *, final: bool
    ) -> None:
        problems = assembly_problems(self._store, episode_id, scenes, episode, final=final)
        if problems:
            kind = "render final incompleto" if final else "montagem incompleta"
            raise AssemblyError(f"{kind} ({len(problems)}): " + "; ".join(problems))

    def _write_episode(self, episode_id: str, episode: EpisodeManifest) -> bool:
        path = self._store.path(episode_id, Constants.EPISODE)
        data = episode.model_dump_json(indent=2).encode("utf-8")
        if path.is_file() and path.read_bytes() == data:
            return False  # o mesmo `episode.json` não se regrava (e não pede o guard)
        self._guard.check(episode_id, Constants.EPISODE, data)
        write_atomic(path, data)
        return True
