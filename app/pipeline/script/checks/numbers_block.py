"""Bloco de números do outline (#170), `used_in_scenes` dos ativos e o perfil do nicho (ADR 031, D)."""

from __future__ import annotations

from app.pipeline.constants.numbers_constants import NumbersConstants
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import effective_shots
from app.pipeline.script.check_assets import episode_assets
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.script.numbers import (
    FormatBrief,
    current_block,
    format_warnings,
    render_block,
    script_numbers,
    used_in_scenes_mismatches,
)
from app.pipeline.script.reading import read_optional


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is None:
        return
    store, episode_id, scenes = episode.store, episode.episode_id, episode.scenes
    assets = episode_assets(store, episode_id)
    brief = read_optional(store, episode_id, NumbersConstants.FORMAT_FILE, FormatBrief, report)
    try:
        numbers = script_numbers(scenes, assets, episode.chars_per_second)
    except ValueError:
        return  # âncora fora de ordem: o erro já está no relatório
    outline = store.path(episode_id, "outline.md")
    block = current_block(outline.read_text(encoding="utf-8")) if outline.is_file() else None
    shots = (shot for scene in scenes.scenes for shot in effective_shots(scene))
    chosen = any(getattr(shot, "asset_id", None) for shot in shots)
    command = f"rode `vp numeros {episode_id} --escrever`"
    if block is not None and block != render_block(numbers, brief, episode.chars_per_second):
        report.warnings.append(f"outline.md: bloco de números desatualizado ({command})")
    elif block is None and chosen and outline.is_file():
        report.warnings.append(f"outline.md: sem o bloco de números ({command})")
    for asset_id, right in used_in_scenes_mismatches(numbers, assets).items():
        listed = list(assets[asset_id].used_in_scenes)
        report.warnings.append(f"assets/{asset_id}.json: used_in_scenes diz {listed}, o roteiro usa {right}")
    report.warnings += format_warnings(numbers, brief)
