"""`vp reopen`: reabre um gate aprovado, com motivo e autor no review.json (§2.6)."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from app.commands.reviewer import default_reviewer
from app.pipeline.ports import Context
from app.pipeline.reopen import reopen_gate
from app.pipeline.schemas import Step


def run(args: argparse.Namespace, context: Context) -> int:
    entry = reopen_gate(
        context.store,
        context.review,
        args.episode_id,
        Step(args.step),
        reviewer=args.reviewer or default_reviewer(Path.cwd()),
        reason=args.reason,
        now=lambda: datetime.now().astimezone().replace(microsecond=0),
        asset_id=args.asset,
    )
    print(f"reaberto: {entry.asset_id or entry.step.value} por {entry.reviewer}")
    return 0
