"""Busca e entrada de ativos de banco de imagem (RF5, §8, ADR 007, ADR 044).

**Busca** (`search_archives`): a falha de um banco (cota, serviço, resposta inválida) é registrada com o
motivo e os outros seguem; "sem resultado" é lista vazia sem falha, e "nenhum banco disponível" é
`NoArchiveAvailable`, com o porquê de cada um. Provedor pago bloqueado (`PaidApiBlocked`) é violação da regra
de custo zero (§2.1) e interrompe a busca; erro de programação também sobe.

**Entrada** (`AssetIntake`): baixa o ativo escolhido para uma cena, com o episódio travado.

- Mídia nova vai para um temporário ao lado do destino e só então para o lugar; o `assets/<id>.json` vai por
  último. Falha antes dele deixa uma mídia sem JSON, que a próxima entrada do mesmo id sobrescreve.
- Ativo já baixado e íntegro (o `sha256` do JSON bate) não é baixado de novo: a cena entra em `used_in_scenes`
  sem apagar as anteriores, e repetir a mesma escolha não escreve nada.
- Ativo aprovado (status de topo ou decisão do gate 3) nunca é alterado: nem JSON, nem mídia. O uso em outra
  cena fica só no `asset_id` do `scenes.json` (como `vp numeros` já faz). Aprovado com a mídia ausente ou
  diferente do `sha256` é erro explícito: reabrir (`vp reopen --step assets --asset <id>`) antes de refazer.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from urllib.parse import urlparse

from app.errors import PipelineError
from app.pipeline.constants.assets_constants import AssetsConstants as Constants
from app.pipeline.file_hash import sha256_file
from app.pipeline.models.archive_availability import ArchiveAvailability
from app.pipeline.models.asset import Asset
from app.pipeline.models.intake_action import IntakeAction
from app.pipeline.models.intake_result import IntakeResult
from app.pipeline.models.search_failure import SearchFailure
from app.pipeline.models.search_result import SearchResult
from app.pipeline.models.status import Status
from app.pipeline.ports import ImmutableManifest, ManifestStore, WriteGuard
from app.providers.archives.base import ArchiveProvider, AssetQuery
from app.providers.errors import PaidApiBlocked, ProviderError


class NoArchiveAvailable(PipelineError, RuntimeError):
    """Nenhum banco da cascata pôde ser usado; a mensagem diz por que cada um foi pulado."""


class AssetError(PipelineError, ValueError):
    """Ativo que não pode ser recebido (mídia vazia, aprovado sem a mídia); nada foi alterado."""


def require_archives(availability: ArchiveAvailability) -> tuple[ArchiveProvider, ...]:
    if not availability.archives:
        why = "; ".join(f"{s.name}: {s.reason}" for s in availability.skipped) or "cascata vazia"
        raise NoArchiveAvailable(f"nenhum banco disponível ({why})")
    return availability.archives


def search_archives(archives: Sequence[ArchiveProvider], query: AssetQuery) -> SearchResult:
    result = SearchResult()
    for archive in archives:
        try:
            found = archive.search_assets(query)
        except PaidApiBlocked:
            raise  # não é indisponibilidade: é a regra de custo zero (§2.1)
        except ProviderError as error:
            result.failures.append(SearchFailure(archive.info.name, query.text, error.reason, str(error)))
            continue
        result.hits.extend((archive.info.name, candidate) for candidate in found)
    return result


def media_suffix(asset: Asset) -> str:
    suffix = Path(urlparse(asset.original_url or "").path).suffix.lower()
    if suffix in Constants.MEDIA_SUFFIXES:
        return suffix
    is_video = Constants.VIDEO_MARK in asset.id
    return Constants.DEFAULT_VIDEO_SUFFIX if is_video else Constants.DEFAULT_PHOTO_SUFFIX


class AssetIntake:
    def __init__(self, store: ManifestStore, guard: WriteGuard) -> None:
        self._store, self._guard = store, guard

    def take(self, episode_id: str, asset: Asset, scene_id: str, archive: ArchiveProvider) -> IntakeResult:
        with self._store.lock(episode_id):
            name = f"assets/{asset.id}.json"
            if not self._store.exists(episode_id, name):
                return self._fetch(episode_id, asset, scene_id, archive, IntakeAction.DOWNLOADED)
            existing = self._store.read(episode_id, name, Asset)
            intact = self._intact(episode_id, existing)
            if self._approved(episode_id, name, existing):
                if not intact:
                    raise AssetError(
                        f"{asset.id}: aprovado, mas a mídia sumiu ou não bate com o sha256; "
                        f"reabra com `vp reopen --step assets --asset {asset.id}`"
                    )
                return IntakeResult(existing, IntakeAction.APPROVED_UNTOUCHED)
            if not intact:
                return self._fetch(episode_id, existing, scene_id, archive, IntakeAction.REPAIRED)
            if scene_id in existing.used_in_scenes:
                return IntakeResult(existing, IntakeAction.UNCHANGED)
            updated = existing.model_copy(update={"used_in_scenes": [*existing.used_in_scenes, scene_id]})
            self._publish_json(episode_id, name, updated)
            return IntakeResult(updated, IntakeAction.SCENE_ADDED)

    def _approved(self, episode_id: str, name: str, asset: Asset) -> bool:
        """Aprovado pelo status do JSON ou por uma decisão do gate 3 ainda válida (o guard recusa mudar)."""
        if asset.review_status is Status.APPROVED:
            return True
        try:
            self._guard.check(episode_id, name)
        except ImmutableManifest:
            return True
        return False

    def _media(self, episode_id: str, asset_id: str) -> Path | None:
        for suffix in Constants.MEDIA_SUFFIXES:
            path = self._store.path(episode_id, f"assets/{asset_id}{suffix}")
            if path.is_file():
                return path
        return None

    def _intact(self, episode_id: str, asset: Asset) -> bool:
        media = self._media(episode_id, asset.id)
        return media is not None and asset.sha256 is not None and sha256_file(media) == asset.sha256

    def _fetch(
        self, episode_id: str, asset: Asset, scene_id: str, archive: ArchiveProvider, action: IntakeAction
    ) -> IntakeResult:
        name = f"assets/{asset.id}.json"
        final = self._store.path(episode_id, f"assets/{asset.id}{media_suffix(asset)}")
        incoming = final.with_name(f".{asset.id}.incoming{final.suffix}")
        incoming.unlink(missing_ok=True)
        try:
            archive.download_asset(asset, incoming)
            if not incoming.is_file() or incoming.stat().st_size == 0:
                raise AssetError(f"{asset.id}: o banco devolveu um arquivo vazio")
            scenes = list(asset.used_in_scenes)
            if scene_id not in scenes:
                scenes.append(scene_id)
            stored = asset.model_copy(update={"sha256": sha256_file(incoming), "used_in_scenes": scenes})
            self._guard.check(episode_id, name, (stored.model_dump_json(indent=2) + "\n").encode())
            stale = self._media(episode_id, asset.id)
            if stale is not None and stale != final:
                stale.unlink()  # a mídia de outra extensão, de uma tentativa anterior
            incoming.replace(final)
        finally:
            incoming.unlink(missing_ok=True)
        self._publish_json(episode_id, name, stored)  # por último: o ativo só existe agora
        return IntakeResult(stored, action)

    def _publish_json(self, episode_id: str, name: str, asset: Asset) -> None:
        self._guard.check(episode_id, name, (asset.model_dump_json(indent=2) + "\n").encode())
        self._store.write(episode_id, name, asset)
