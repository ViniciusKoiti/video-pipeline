"""Plano da trilha (ADR 030), quando o episódio tem `music.json`."""

from __future__ import annotations

from app.media.narration import timeline_length
from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import MusicPlan
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.script.reading import read_optional
from app.pipeline.sound.music import plan_problems


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is None:
        return
    store, episode_id = episode.store, episode.episode_id
    plan = read_optional(store, episode_id, SchemasConstants.MUSIC_PLAN_FILE, MusicPlan, report)
    if plan is None:
        return
    if episode.music_catalog is None:
        report.errors.append("music.json sem catálogo de faixas (data/music/catalog.json)")
        return
    minutes = sum(timeline_length(s.narration) for s in episode.scenes.scenes) / episode.chars_per_second / 60
    errors, warnings = plan_problems(plan, episode.scenes.scenes, episode.music_catalog, minutes)
    report.errors += errors
    report.warnings += warnings
    tracks = sorted({cue.track for cue in plan.cues if cue.track})
    report.warnings += [
        f"music.json: faixa {t} ainda sem cópia no episódio (assets/{t}.json, gate 3)"
        for t in tracks
        if not store.exists(episode_id, f"assets/{t}.json")
    ]
    if plan.end_tail_ms:
        _end_tail(plan, episode.scenes.scenes[-1].id, report)
    if not errors:
        report.checked.append(f"trilha: {len(plan.cues)} entrada(s), {len(tracks)} faixa(s)")


def _end_tail(plan: MusicPlan, last_scene: str, report: CheckReport) -> None:
    """A cauda da tela final (emenda de 2026-11-23 da ADR 030) pede um fundo até o fim da última cena."""
    if not any(
        c.track and c.role != "sting" and c.end.scene == last_scene and c.end.text is None for c in plan.cues
    ):
        report.errors.append(f"music.json: cauda (end_tail_ms) sem fundo que vá até o fim da {last_scene}")
    report.warnings.append(
        f"music.json: cauda de {plan.end_tail_ms / 1000:.0f} s só de trilha depois da última fala "
        "(tela final); vale na montagem pelo kit, e o vp render ainda corta no fim da voz"
    )
