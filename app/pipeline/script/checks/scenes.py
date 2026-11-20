"""As cenas do `scenes.json`: as regras por cena e por plano, na ordem em que entram no relatório (ADR 064).

Regra nova que olha uma cena entra em `SCENE_RULES`; a que olha um plano, em `PLAN_RULES`. Cada plano chega
com a duração estimada pela narração, a mesma conta do bloco de números (#170).
"""

from __future__ import annotations

from collections.abc import Callable

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import Scene, effective_shots, unknown_source_refs
from app.pipeline.script.checks import (
    arithmetic,
    calculation,
    claims,
    map_codes,
    number_format,
    plan_timing,
    quote_text,
    text_fit,
)
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.script.models.plan_check import PlanCheck
from app.pipeline.script.numbers import scene_duration_ms, scene_timings

SceneRule = Callable[[Scene, CheckedEpisode, CheckReport], None]
PlanRule = Callable[[PlanCheck, CheckReport], None]

SCENE_RULES: tuple[SceneRule, ...] = (claims.check,)
PLAN_RULES: tuple[PlanRule, ...] = (
    text_fit.check,
    number_format.check,
    arithmetic.check,
    calculation.check,
    plan_timing.check,
    map_codes.check,
    quote_text.check,
)


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    """Valida as cenas e guarda em `episode.planned` cada plano com a duração estimada (para as citações)."""
    scenes = episode.scenes
    if scenes is None:
        return
    if episode.sources is not None:
        report.errors += unknown_source_refs(scenes, episode.sources)
    # sem objetivo declarado (já é alerta), a conta não é recusada por ele
    explains = scenes.objective is None or "explicar" in scenes.objective.kinds
    total_ms, shots = 0.0, 0
    for scene in scenes.scenes:
        for scene_rule in SCENE_RULES:
            scene_rule(scene, episode, report)
        total_ms += scene_duration_ms(scene, episode.chars_per_second)
        shots += len(effective_shots(scene))
        try:
            timed = scene_timings(scene, episode.chars_per_second)
        except ValueError as error:
            report.errors.append(f"{scene.id}: {error}")
            continue
        media_before = False  # foto ou B-roll da cena já na tela: tarja, número e carimbo vão por cima
        for shot, _, ms in timed:
            episode.planned.append((scene.id, shot, ms))
            over_media = media_before and shot.kind in SchemasConstants.OVERLAY_SHOT_KINDS
            plan = PlanCheck(
                scene.id, shot, ms, over_media, scenes.language, explains,
                episode.region_codes, episode.excerpts,
            )
            for plan_rule in PLAN_RULES:
                plan_rule(plan, report)
            media_before = media_before or shot.kind in SchemasConstants.MEDIA_SHOT_KINDS
    report.checked.append(
        f"scenes.json: {len(scenes.scenes)} cena(s), {shots} plano(s), ~{total_ms / 1000:.0f} s de narração "
        f"(média ~{total_ms / shots / 1000:.1f} s por plano, estimada)"
    )
