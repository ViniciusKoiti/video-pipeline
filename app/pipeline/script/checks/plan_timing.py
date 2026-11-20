"""Tempo de cada plano pela narração: curto ou longo demais, ou sem tempo para ser lido (ADR 008 e 011)."""

from __future__ import annotations

from app.pipeline.constants.check_constants import CheckConstants as Constants
from app.pipeline.constants.numbers_constants import NumbersConstants
from app.pipeline.constants.shots_constants import ShotsConstants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import QuoteShot, Shot
from app.pipeline.script.models.plan_check import PlanCheck


def _needs_reading_time(shot: Shot) -> bool:
    return shot.kind in Constants.READING_KINDS or (isinstance(shot, QuoteShot) and shot.style == "document")


def check(plan: PlanCheck, report: CheckReport) -> None:
    shot, ms = plan.shot, plan.ms
    too_long = ms > NumbersConstants.MAX_SHOT_MS and shot.kind not in NumbersConstants.LONG_KINDS
    if ms < ShotsConstants.MIN_SHOT_MS or too_long:
        report.warnings.append(f"{plan.scene_id}: plano {shot.kind} ({shot.anchor!r}) com ~{ms / 1000:.1f} s")
    elif ms < Constants.READING_MS and _needs_reading_time(shot):
        report.warnings.append(
            f"{plan.scene_id}: {shot.kind} ({shot.anchor!r}) com ~{ms / 1000:.1f} s; "
            f"precisa de {Constants.READING_MS / 1000:.0f} s para ser lido"
        )
