"""Frase afirmativa em cena sem `claims` (ADR 031): alerta, salvo na ficção histórica (ADR 055)."""

from __future__ import annotations

from app.pipeline.models.check_report import CheckReport
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.script.molde import claimless_statements


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is not None:
        report.warnings += claimless_statements(episode.scenes)
