"""Forma do roteiro longo contra o molde do nicho copiado no episódio pela partitura (ADR 031). Só alertas: o
molde é descrição de amostra e nunca fonte de fato."""

from __future__ import annotations

from app.pipeline.constants.molde_constants import MoldeConstants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.script.molde import Molde, molde_summary, molde_warnings
from app.pipeline.script.reading import read_optional


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is None:
        return
    molde = read_optional(episode.store, episode.episode_id, MoldeConstants.MOLDE_FILE, Molde, report)
    if molde is None:
        return
    report.checked.append(molde_summary(molde))
    report.warnings += molde_warnings(episode.scenes, molde, episode.chars_per_second)
