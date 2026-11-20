"""Conta na tela (cálculo, nota com total) só em vídeo que explica (ADR 020)."""

from __future__ import annotations

from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import CalculationShot, ReceiptShot
from app.pipeline.script.models.plan_check import PlanCheck


def check(plan: PlanCheck, report: CheckReport) -> None:
    shot = plan.shot
    computed = isinstance(shot, CalculationShot) or (isinstance(shot, ReceiptShot) and shot.total)
    if computed and not plan.explains:
        report.errors.append(
            f"{plan.scene_id}: {shot.kind} ({shot.anchor!r}): conta na tela só em vídeo que explica "
            "(ADR 020)"
        )
