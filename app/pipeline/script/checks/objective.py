"""O objetivo do vídeo no roteiro (ADR 019): falta dele e notícia velha são alerta; o resumo mostra tipos e
promessa. Saiu de `check.py` (gate de tamanho)."""

from __future__ import annotations

from datetime import date

from app.pipeline.constants.check_constants import CheckConstants as Constants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import ScenesManifest
from app.pipeline.script.models.checked_episode import CheckedEpisode


def objective_warnings(scenes: ScenesManifest, today: date | None = None) -> list[str]:
    """O objetivo do vídeo (ADR 019): alerta quando falta, e quando o fato noticiado já é velho."""
    objective = scenes.objective
    if objective is None:
        return ["roteiro sem objetivo declarado (noticiar, explicar ou opinar; ADR 019)"]
    if "noticiar" in objective.kinds and objective.event_date is not None and today is not None:
        age = (today - objective.event_date).days
        when = f"{objective.event_date:%d/%m/%Y}"
        if age < 0:
            return [f"objetivo noticiar com data no futuro ({when})"]
        if age > Constants.NEWS_MAX_AGE_DAYS:
            return [
                (
        f'objetivo noticiar, mas o fato é de {when} ({age} dias): depois de '
        f'{Constants.NEWS_MAX_AGE_DAYS} dias não é notícia; o vídeo explica ou opina'
    )
            ]
    return []


def objective_summary(scenes: ScenesManifest) -> str | None:
    objective = scenes.objective
    if objective is None:
        return None
    return f"objetivo: {' + '.join(objective.kinds)}: {objective.promise}"


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is None:
        return
    if (summary := objective_summary(episode.scenes)) is not None:
        report.checked.append(summary)
    report.warnings += objective_warnings(episode.scenes, episode.today)
