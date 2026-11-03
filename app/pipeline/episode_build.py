"""O `episode.json` de um episódio explicativo a partir do `scenes.json` e das falas (RF7; era o miolo do
`montar_episodio.py`).

- **Cenas:** a duração real de cada WAV (ffprobe) vira o tempo dos planos (`app/pipeline/shots.py`), em
  sequência, sem sobreposição. A mídia de cada plano de foto ou B-roll é `assets/<asset_id>.<ext>`; com
  `sources.json`, cada plano com claims ganha a fonte do rodapé (ADR 011).
- **Trilha (ADR 030):** com `music.json` na pasta, cada entrada vira um trecho de `music` no `episode.json`,
  com o tempo tirado dos WAVs; a faixa é `assets/<asset_id>.<ext>`, copiada do catálogo por `vp music usar`.
- Nada aqui grava arquivo: quem monta o episódio é o `EpisodeRenderer` (ADR 051). Falta de mídia ou de
  catálogo é `EpisodeBuildError` com a mensagem do que falta.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.errors import PipelineError
from app.media.constants.captions_constants import CaptionsConstants
from app.media.probe import duration_ms
from app.pipeline.constants.episode_build_constants import EpisodeBuildConstants as Constants
from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.music import load_music_catalog, resolve_music
from app.pipeline.schemas import (
    EpisodeFormat,
    EpisodeManifest,
    EpisodeMusic,
    EpisodeScene,
    MusicPlan,
    ScenesManifest,
    Shot,
    SourcesManifest,
    VideoSpec,
)
from app.pipeline.shots import episode_shots


class EpisodeBuildError(PipelineError, ValueError):
    """Mídia, faixa ou catálogo que falta para montar o episódio; a mensagem diz qual."""


def _asset_file(episode_dir: Path, asset_id: str, suffixes: tuple[str, ...]) -> str | None:
    for suffix in suffixes:
        if (episode_dir / "assets" / f"{asset_id}{suffix}").is_file():
            return f"assets/{asset_id}{suffix}"
    return None


def media_path(episode_dir: Path, asset_id: str) -> str:
    found = _asset_file(episode_dir, asset_id, Constants.MEDIA_SUFFIXES)
    if found is None:
        raise EpisodeBuildError(f"ativo {asset_id} sem arquivo de mídia em assets/")
    return found


def _media_for(episode_dir: Path) -> Callable[[Shot], str | None]:
    def media_for(shot: Shot) -> str | None:
        asset_id = getattr(shot, "asset_id", None)
        if not asset_id:
            raise EpisodeBuildError(f"plano {shot.kind} sem asset_id: escolha o ativo no gate 3")
        return media_path(episode_dir, asset_id)

    return media_for


def build_scenes(
    scenes: ScenesManifest,
    wavs: dict[str, Path],
    episode_dir: Path,
    sources: SourcesManifest | None,
    measure: Callable[[Path], int] = duration_ms,
) -> list[EpisodeScene]:
    """As cenas com o tempo da voz real, em sequência: uma por cena do roteiro, na ordem."""
    built, cursor = [], 0
    for scene in scenes.scenes:
        wav = wavs[scene.id]
        try:
            audio = wav.resolve().relative_to(episode_dir.resolve()).as_posix()
        except ValueError as error:
            raise EpisodeBuildError(f"fala {scene.id} fora da pasta do episódio: {wav}") from error
        ms = measure(wav)
        shots = episode_shots(scene, ms, _media_for(episode_dir), sources, scenes.language)
        built.append(
            EpisodeScene(
                id=scene.id,
                start_ms=cursor,
                duration_ms=ms,
                narration=scene.narration,
                audio=audio,
                shots=shots,
                host_corner=scene.host_corner,
                delivery=scene.delivery,
            )
        )
        cursor += ms
    return built


def build_episode(scenes: ScenesManifest, episode_scenes: list[EpisodeScene]) -> EpisodeManifest:
    """O `episode.json` v2 do explicativo, sem trilha."""
    return EpisodeManifest(
        schema_version=2,
        episode_id=scenes.episode_id,
        title=Constants.DRAFT_TITLE.format(episode_id=scenes.episode_id),
        language=scenes.language,
        format=EpisodeFormat.EXPLAINER,
        scenes=episode_scenes,
        host=scenes.host,
        series=scenes.series,
        video=VideoSpec.for_orientation(scenes.orientation),
        captions=CaptionsConstants.CAPTIONS,
    )


def music_segments(data_dir: Path, episode_dir: Path, episode: EpisodeManifest) -> list[EpisodeMusic]:
    """Trechos da trilha com o tempo dos WAVs; sem `music.json`, nenhum."""
    plan_path = episode_dir / SchemasConstants.MUSIC_PLAN_FILE
    if not plan_path.is_file():
        return []
    catalog = load_music_catalog(data_dir)
    if catalog is None:
        raise EpisodeBuildError("music.json sem catálogo de faixas (data/music/catalog.json)")

    def track_file(asset_id: str) -> str:
        if not (episode_dir / "assets" / f"{asset_id}.json").is_file():
            raise EpisodeBuildError(f"faixa {asset_id} sem ativo no episódio (vp music usar)")
        found = _asset_file(episode_dir, asset_id, Constants.MUSIC_SUFFIXES)
        if found is None:
            raise EpisodeBuildError(f"faixa {asset_id} sem arquivo de áudio em assets/")
        return found

    plan = MusicPlan.model_validate_json(plan_path.read_text())
    return resolve_music(plan, episode, catalog, track_file)


def with_music(episode: EpisodeManifest, tracks: list[EpisodeMusic]) -> EpisodeManifest:
    """O mesmo episódio com a trilha; sem trilha, devolve o próprio."""
    if not tracks:
        return episode
    return EpisodeManifest.model_validate({**episode.model_dump(), "music": tracks})
