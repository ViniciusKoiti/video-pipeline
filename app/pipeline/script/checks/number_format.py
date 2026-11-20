"""Número na tela fora da convenção do idioma do episódio (ADR 011, emenda "número por idioma")."""

from __future__ import annotations

from app.pipeline.constants.check_constants import CheckConstants as Constants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import (
    CalculationShot,
    ChartShot,
    CompareShot,
    Language,
    NumberShot,
    ReceiptShot,
    Shot,
    number_format_problem,
)
from app.pipeline.script.models.plan_check import PlanCheck


def number_errors(scene_id: str, shot: Shot, language: Language) -> list[str]:
    """Número na tela fora da convenção do idioma do episódio, ou que o template não sabe formatar nele
    (ADR 011, emenda "número por idioma"). Escrito errado, o hodômetro mostraria outro valor."""
    values: list[str] = []
    if isinstance(shot, NumberShot):
        values = [shot.value]
    elif isinstance(shot, CompareShot):
        values = [shot.left.value, shot.right.value]
    elif isinstance(shot, CalculationShot):
        values = [term.text for term in shot.terms] + [shot.result.text]
    elif isinstance(shot, ReceiptShot):
        values = [item.value for item in shot.items] + ([shot.total.value] if shot.total else [])
    errors = [
        f"{scene_id}: {shot.kind} ({shot.anchor!r}): {problem}"
        for value in values
        if (problem := number_format_problem(value, language))
    ]
    if (
        language == "en"
        and isinstance(shot, ChartShot)
        and shot.type in Constants.BAR_TYPES
        and any(abs(p.value) >= Constants.BAR_PLAIN_BELOW or p.value != round(p.value) for p in shot.points)
    ):
        errors.append(
            f"{scene_id}: gráfico de barras ({shot.anchor!r}) em inglês com valor que o motion-kit fixado "
            "formata em pt-BR; use inteiros abaixo de mil ou outro tipo de gráfico"
        )
    return errors


def check(plan: PlanCheck, report: CheckReport) -> None:
    report.errors += number_errors(plan.scene_id, plan.shot, plan.language)
