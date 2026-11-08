"""`vp numeros`: números do roteiro e comparação com o nicho -> `outline.md` e `plano-imagens.md` (#170)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.pipeline.check import episode_assets
from app.pipeline.constants.numbers_constants import NumbersConstants
from app.pipeline.numbers import (
    FormatBrief,
    current_block,
    render_block,
    render_image_plan,
    replace_block,
    script_numbers,
    used_in_scenes_mismatches,
)
from app.pipeline.ports import Context
from app.pipeline.schemas import ScenesManifest, Status
from app.settings import speech_chars_per_second


def _write_if_changed(path: Path, text: str) -> bool:
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def run(args: argparse.Namespace, context: Context) -> int:
    store, episode_id = context.store, args.episode_id
    chars_per_second = speech_chars_per_second(context.settings)
    scenes = store.read(episode_id, "scenes.json", ScenesManifest)
    assets = episode_assets(store, episode_id)
    brief = None
    if store.exists(episode_id, NumbersConstants.FORMAT_FILE):
        brief = store.read(episode_id, NumbersConstants.FORMAT_FILE, FormatBrief)
    try:
        numbers = script_numbers(scenes, assets, chars_per_second)
    except ValueError as error:
        print(f"vp numeros: {error} (rode vp check)", file=sys.stderr)
        return 1
    block = render_block(numbers, brief, chars_per_second)
    plan = render_image_plan(scenes, numbers, assets, chars_per_second)
    outline, plan_path = (
        store.path(episode_id, "outline.md"),
        store.path(episode_id, NumbersConstants.IMAGE_PLAN_FILE),
    )
    print(block)
    if not outline.is_file():
        print("outline.md: não existe", file=sys.stderr)
        return 1
    text = outline.read_text(encoding="utf-8")
    current = current_block(text)
    state = "em dia" if current == block else ("desatualizado" if current else "sem o bloco")
    plan_ok = plan_path.is_file() and plan_path.read_text(encoding="utf-8") == plan
    print(f"outline.md: {state}; {NumbersConstants.IMAGE_PLAN_FILE}: {'em dia' if plan_ok else 'diferente'}")
    with store.lock(episode_id):
        if args.escrever:
            targets = (
                ("outline.md", outline, replace_block(text, block)),
                (NumbersConstants.IMAGE_PLAN_FILE, plan_path, plan),
            )
            wrote = [name for name, path, new in targets if _write_if_changed(path, new)]
            print("gravado: " + (", ".join(wrote) if wrote else "nada mudou"))
        if args.used_in_scenes:
            for asset_id, used in used_in_scenes_mismatches(numbers, assets).items():
                asset = assets[asset_id]
                if asset.review_status is Status.APPROVED:
                    print(f"{asset_id}: aprovado, não mudo (o roteiro usa {used})")
                    continue
                updated = asset.model_copy(update={"used_in_scenes": used})
                store.write(episode_id, f"assets/{asset_id}.json", updated)
                print(f"{asset_id}: used_in_scenes -> {used}")
    return 0
