"""Mapa que destaca código fora dos contornos que o template sabe desenhar."""

from __future__ import annotations

from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import MapShot
from app.pipeline.script.models.plan_check import PlanCheck


def check(plan: PlanCheck, report: CheckReport) -> None:
    if isinstance(plan.shot, MapShot) and plan.region_codes is not None:
        for code in plan.shot.highlight:
            if code not in plan.region_codes:
                report.errors.append(f"{plan.scene_id}: código {code} fora dos contornos do mapa")
