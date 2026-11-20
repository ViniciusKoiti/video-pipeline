"""Citação de obra (`Citacao`, ADR 007) nos planos de mídia: teto por vídeo e por quadro."""

from __future__ import annotations

from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import citation_violations
from app.pipeline.script.check_assets import planned_assets
from app.pipeline.script.models.checked_episode import CheckedEpisode


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is None:
        return
    assets = planned_assets(episode.store, episode.episode_id, episode.planned, report)
    report.errors += citation_violations(episode.planned, assets)
