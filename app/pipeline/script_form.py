"""Forma do roteiro no `vp check`: objetivo (ADR 019), funil (ADR 026), opinião sem rótulo, lacuna dita na
fala, frase de fato sem claim e relógio de retenção (ADR 061). Cada conferência mora no seu módulo; aqui elas
entram no relatório, cada uma no seu nível (erro, alerta ou ponto de atenção para o gate 2)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from app.pipeline.funnel_check import funnel_attention, funnel_errors, funnel_summary, funnel_warnings
from app.pipeline.models.check_report import CheckReport
from app.pipeline.molde import claimless_statements
from app.pipeline.narration_gaps import gap_warnings
from app.pipeline.objective_check import objective_summary, objective_warnings
from app.pipeline.opinion_labels import opinion_label_errors
from app.pipeline.retention_clock import pause_hints, retention_attention, retention_summary, scene_clock
from app.pipeline.schemas import ScenesManifest


def check_script_form(
    report: CheckReport,
    scenes: ScenesManifest,
    chars_per_second: float,
    today: date | None,
    measured: Mapping[str, float] | None = None,
) -> None:
    """`measured`: segundos da voz real por cena, quando todas já têm WAV; sem ele, o relógio estima."""
    timed, source = scene_clock(scenes, chars_per_second, measured)
    for summary in (objective_summary(scenes), funnel_summary(scenes), retention_summary(timed, source)):
        if summary is not None:
            report.checked.append(summary)
    report.errors += funnel_errors(scenes) + opinion_label_errors(scenes)
    report.warnings += objective_warnings(scenes, today) + funnel_warnings(scenes)
    report.warnings += claimless_statements(scenes) + gap_warnings(scenes) + pause_hints(timed)
    report.attention += funnel_attention(scenes, chars_per_second) + retention_attention(timed, source)
