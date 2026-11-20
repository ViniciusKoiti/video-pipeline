"""Citação na tela que não está nos trechos que ela cita (ADR 009)."""

from __future__ import annotations

from app.pipeline.excerpts import quote_in_excerpt
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import QuoteShot
from app.pipeline.script.models.plan_check import PlanCheck


def check(plan: PlanCheck, report: CheckReport) -> None:
    shot, excerpts = plan.shot, plan.excerpts
    if isinstance(shot, QuoteShot) and excerpts:
        cited = [excerpts[e] for c in shot.claims for e in c.excerpt_ids if e in excerpts]
        if cited and not any(quote_in_excerpt(shot.text, text) for text in cited):
            report.errors.append(
                f"{plan.scene_id}: citação na tela não está nos trechos citados: {shot.text!r}"
            )
