"""Forma do roteiro no `vp check`: objetivo (ADR 019), funil (ADR 026), opinião sem rótulo, lacuna dita na
fala, frase de fato sem claim, relógio de retenção (ADR 061) e trava fonética (glossário e pausas). Cada
conferência mora no seu módulo; aqui elas entram no relatório, cada uma no seu nível (erro, alerta ou ponto de
atenção para o gate 2)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path

from app.media.pronunciation import load_glossary
from app.pipeline.funnel_check import funnel_attention, funnel_errors, funnel_summary, funnel_warnings
from app.pipeline.glossary_check import colon_pause_warnings, glossary_attention
from app.pipeline.models.check_report import CheckReport
from app.pipeline.molde import claimless_statements
from app.pipeline.narration_gaps import gap_warnings
from app.pipeline.objective_check import objective_summary, objective_warnings
from app.pipeline.opinion_labels import opinion_label_errors
from app.pipeline.ports import ManifestStore
from app.pipeline.retention_clock import pause_hints, retention_attention, retention_summary, scene_clock
from app.pipeline.schemas import ScenesManifest
from app.pipeline.voice_timeline import measured_seconds


def check_script_form(
    report: CheckReport,
    scenes: ScenesManifest,
    store: ManifestStore,
    episode_id: str,
    chars_per_second: float,
    today: date | None,
    measure: Callable[[Path], float] | None = None,
    final_voice: str | None = None,
) -> None:
    """`measure`: segundos de um WAV; com ele e a voz de todas as cenas pronta, o relógio usa a voz real.
    `final_voice`: a voz do vídeo final, para as regras do glossário por voz."""
    ids = [scene.id for scene in scenes.scenes]
    measured = measured_seconds(store, episode_id, ids, measure) if measure else None
    timed, source = scene_clock(scenes, chars_per_second, measured)
    glossary = load_glossary(store.path(episode_id, ""))
    for summary in (objective_summary(scenes), funnel_summary(scenes), retention_summary(timed, source)):
        if summary is not None:
            report.checked.append(summary)
    report.errors += funnel_errors(scenes) + opinion_label_errors(scenes)
    report.warnings += objective_warnings(scenes, today) + funnel_warnings(scenes)
    report.warnings += claimless_statements(scenes) + gap_warnings(scenes) + pause_hints(timed)
    report.warnings += colon_pause_warnings(scenes)
    report.attention += funnel_attention(scenes, chars_per_second) + retention_attention(timed, source)
    report.attention += glossary_attention(scenes, glossary, final_voice)
