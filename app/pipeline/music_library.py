"""O catálogo de música de fundo e a entrada de uma faixa no episódio (RF5, ADR 030, ADR 047).

**Adicionar** (`add_track`): a faixa baixada da YouTube Audio Library vai para `data/music/` com o ativo
`<id>.json` (licença, `sha256`, `usage_notes`) e uma linha no `catalog.json`. Nunca substitui uma faixa do
catálogo (id repetido é erro); licença fora da lista e faixa CC sem atribuição são recusadas antes de
copiar. Mídia, ativo e `catalog.json` são gravados nessa ordem, cada um inteiro, e a faixa só existe no
catálogo depois do último: a sobra de uma tentativa que parou antes é sobrescrita na seguinte.

**Instalar** (`install_track`): copia o ativo e o arquivo para `assets/` do episódio, onde o gate 3 os aprova.
O arquivo do catálogo tem de bater com o `sha256` do ativo (senão o registro de licença não vale para ele).
Nada que o episódio já tem é trocado: a mesma faixa não escreve nada, outra versão com o mesmo id é erro, e
ativo aprovado com a mídia ausente ou diferente é erro explícito (reabrir antes). O ativo vai por último.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

from app.pipeline.atomic_files import write_atomic
from app.pipeline.constants.gates_constants import GatesConstants
from app.pipeline.constants.music_constants import MusicConstants
from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.file_hash import sha256_file
from app.pipeline.models.audio_probe import AudioProbe
from app.pipeline.models.track_draft import TrackDraft
from app.pipeline.models.track_install_action import TrackInstallAction
from app.pipeline.music import MusicCatalogError, load_music_catalog
from app.pipeline.ports import ImmutableManifest, ManifestStore, WriteGuard
from app.pipeline.schemas import Asset, MusicCatalog, MusicTrack, Provider, Status


def slug(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def _check_draft(source: Path, draft: TrackDraft) -> None:
    licenses = {SchemasConstants.AUDIO_LIBRARY_LICENSE} | SchemasConstants.ATTRIBUTION_LICENSES
    if not source.is_file():
        raise MusicCatalogError(f"{source} não existe")
    if source.suffix.lower() not in GatesConstants.AUDIO_SUFFIXES:
        raise MusicCatalogError(f"formato {source.suffix} fora de {', '.join(GatesConstants.AUDIO_SUFFIXES)}")
    if draft.license_id not in licenses:
        raise MusicCatalogError(f"licença {draft.license_id!r} fora de {', '.join(sorted(licenses))}")
    if draft.license_id in SchemasConstants.ATTRIBUTION_LICENSES and not draft.attribution.strip():
        raise MusicCatalogError("faixa CC exige a atribuição (o texto do botão Copy da coluna License type)")
    if not slug(draft.title):
        raise MusicCatalogError("o título não gera um id (só símbolos?)")
    if not any(mood.strip() for mood in draft.moods):
        raise MusicCatalogError("informe ao menos um clima (a escuta é do dono)")
    if draft.bpm is not None and draft.bpm <= 0:
        raise MusicCatalogError(f"bpm deve ser positivo, não {draft.bpm}")


def add_track(
    music_dir: Path, source: Path, draft: TrackDraft, probe: AudioProbe, now: datetime
) -> tuple[MusicTrack, float]:
    """Devolve a faixa registrada e a loudness medida."""
    _check_draft(source, draft)
    asset_id = f"{MusicConstants.ID_PREFIX}{slug(draft.title)}"
    catalog = load_music_catalog(music_dir.parent) or MusicCatalog()
    if asset_id in catalog.by_id():
        raise MusicCatalogError(f"{asset_id} já está no catálogo; o código não substitui faixa")
    target = music_dir / f"{asset_id}{source.suffix.lower()}"
    for orphan in music_dir.glob(f"{asset_id}.*"):  # sobra de uma tentativa que não chegou ao catálogo
        orphan.unlink()
    raw = source.read_bytes()
    write_atomic(target, raw)
    lufs = probe.lufs(target)
    track = _track(draft, asset_id, target.name, probe.duration_ms(target), probe.intensity(lufs))
    write_atomic(
        music_dir / f"{asset_id}.json",
        _asset(draft, asset_id, raw, now).model_dump_json(indent=2).encode() + b"\n",
    )
    updated = MusicCatalog(tracks=[*catalog.tracks, track])
    write_atomic(
        music_dir / SchemasConstants.MUSIC_CATALOG_FILE, updated.model_dump_json(indent=2).encode() + b"\n"
    )
    return track, lufs


def _track(draft: TrackDraft, asset_id: str, file: str, duration_ms: int, intensity: int) -> MusicTrack:
    try:
        return MusicTrack(
            asset_id=asset_id,
            title=draft.title,
            artist=draft.artist,
            file=file,
            duration_ms=duration_ms,
            moods=[m.strip() for m in draft.moods if m.strip()],
            intensity=intensity,
            bpm=draft.bpm,
            vocals=draft.vocals,
            loops=draft.loops,
        )
    except ValidationError as error:
        raise MusicCatalogError(
            f"{asset_id}: {error.errors()[0]['loc']}: {error.errors()[0]['msg']}"
        ) from error


def _asset(draft: TrackDraft, asset_id: str, raw: bytes, now: datetime) -> Asset:
    by = f" de {draft.artist}" if draft.artist else ""
    notes = (
        f'Faixa "{draft.title}"{by}, baixada pelo dono na YouTube Audio Library (Studio) em {now:%Y-%m-%d}; '
        f"licença conforme a coluna License type ({draft.license_id}). Só em vídeo publicado no YouTube "
        f"(data/benchmarks/termos-musica.md, ADR 030). Voz cantada: {'sim' if draft.vocals else 'não'} "
        "(escuta do dono)."
    )
    try:
        return Asset(
            id=asset_id,
            provider=Provider.YOUTUBE_AUDIO_LIBRARY,
            provider_id=draft.title,
            page_url=MusicConstants.LIBRARY_URL,
            author=draft.artist,
            license_id=draft.license_id,
            attribution_text=draft.attribution,
            usage_notes=notes,
            retrieved_at=now,
            sha256=hashlib.sha256(raw).hexdigest(),
        )
    except ValidationError as error:
        raise MusicCatalogError(f"{asset_id}: {error.errors()[0]['msg']}") from error


def install_track(
    store: ManifestStore, guard: WriteGuard, music_dir: Path, episode_id: str, asset_id: str
) -> TrackInstallAction:
    catalog = load_music_catalog(music_dir.parent) or MusicCatalog()
    track = catalog.by_id().get(asset_id)
    if track is None:
        raise MusicCatalogError(f"{asset_id} fora do catálogo")
    asset, media = _catalog_asset(music_dir, track)
    if not store.path(episode_id, "").is_dir():  # o lock criaria a pasta de um episódio que não existe
        raise MusicCatalogError(f"episódio {episode_id} não existe")
    name, media_name = f"assets/{asset_id}.json", f"assets/{track.file}"
    with store.lock(episode_id):
        target = store.path(episode_id, media_name)
        if not store.exists(episode_id, name):
            write_atomic(target, media.read_bytes())
            guard.check(episode_id, name, (asset.model_dump_json(indent=2) + "\n").encode())
            store.write(episode_id, name, asset)  # por último: a faixa só existe no episódio agora
            return TrackInstallAction.INSTALLED
        existing = store.read(episode_id, name, Asset)
        if existing.sha256 != asset.sha256:
            raise MusicCatalogError(
                f"{asset_id}: o episódio já tem outra versão desta faixa (sha256 diferente); "
                "o código não a troca: reabra o ativo e remova a antiga à mão"
            )
        if target.is_file() and sha256_file(target) == asset.sha256:
            return TrackInstallAction.UNCHANGED
        if _approved(guard, episode_id, name, existing):
            raise MusicCatalogError(
                f"{asset_id}: aprovada, mas a mídia sumiu ou não bate com o sha256; "
                f"reabra com `vp reopen --step assets --asset {asset_id}`"
            )
        write_atomic(target, media.read_bytes())
        return TrackInstallAction.REPAIRED


def _catalog_asset(music_dir: Path, track: MusicTrack) -> tuple[Asset, Path]:
    """O ativo e o arquivo da faixa no catálogo, conferidos entre si."""
    json_path, media = music_dir / f"{track.asset_id}.json", music_dir / track.file
    for path in (json_path, media):
        if not path.is_file():
            raise MusicCatalogError(
                f"{track.asset_id}: falta {path.name} em data/{SchemasConstants.MUSIC_DIR}/"
            )
    try:
        asset = Asset.model_validate_json(json_path.read_text(encoding="utf-8"))
    except ValidationError as error:
        raise MusicCatalogError(f"{json_path.name}: fora do contrato ({error.errors()[0]['msg']})") from error
    if sha256_file(media) != asset.sha256:
        raise MusicCatalogError(
            f"{track.asset_id}: {media.name} não bate com o sha256 do ativo (alterado à mão?)"
        )
    return asset, media


def _approved(guard: WriteGuard, episode_id: str, name: str, asset: Asset) -> bool:
    if asset.review_status is Status.APPROVED:
        return True
    try:
        guard.check(episode_id, name)
    except ImmutableManifest:
        return True
    return False
