"""Métricas de publicação (§12), quando o episódio tem `metrics.json`: contrato e janelas vencidas."""

from __future__ import annotations

from datetime import date

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.metrics import summary_line
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import PublicationMetrics
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.script.reading import read_optional


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    name = SchemasConstants.METRICS_FILE
    metrics = read_optional(episode.store, episode.episode_id, name, PublicationMetrics, report)
    if metrics is None:
        return
    today = episode.today or date.today()
    report.checked.append(f"métricas: {summary_line(metrics, today)}")
    report.warnings += [
        f"metrics.json: {w} vencida em {metrics.due_date(w):%Y-%m-%d} e não lida"
        for w in metrics.pending(today)
    ]
