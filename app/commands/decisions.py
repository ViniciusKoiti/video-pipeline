"""`vp approve`, `vp reject` e `vp checagem`: o que o humano decide e o que o verificador diz (ADR 009)."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from app.commands.constants.cli_constants import CliConstants
from app.commands.project_root import project_root
from app.commands.reviewer import default_reviewer
from app.pipeline.check_report import load_check_report
from app.pipeline.gates import record_check, record_decision
from app.pipeline.ports import Context
from app.pipeline.schemas import Decision, Step


def approve(args: argparse.Namespace, context: Context) -> int:
    return _decide(args, context, Decision.APPROVED, args.notes, skip_check=args.skip_check)


def reject(args: argparse.Namespace, context: Context) -> int:
    decision = Decision.CHANGES_REQUESTED if args.changes else Decision.REJECTED
    return _decide(args, context, decision, args.reason)


def _decide(
    args: argparse.Namespace, context: Context, decision: Decision, notes: str, skip_check: str | None = None
) -> int:
    entry = record_decision(
        context.store,
        context.review,
        args.episode_id,
        Step(args.step),
        decision,
        reviewer=args.reviewer or default_reviewer(project_root(Path.cwd())),
        now=lambda: datetime.now().astimezone().replace(microsecond=0),
        asset_id=args.asset,
        notes=notes,
        skip_check=skip_check,
    )
    target = entry.asset_id or entry.step.value
    print(
        f"{CliConstants.DECISION_LABELS[entry.decision]}: {target} por {entry.reviewer} ({entry.input_hash})"
    )
    return 0


def checagem(args: argparse.Namespace, context: Context) -> int:
    verdict, problems = load_check_report(args.parecer)
    entry = record_check(
        context.store,
        args.episode_id,
        verdict,
        problems,
        reviewer=args.reviewer,
        now=lambda: datetime.now().astimezone().replace(microsecond=0),
    )
    label = CliConstants.CHECK_LABELS[entry.verdict]
    print(f"checagem: {label} por {entry.reviewer}, {len(entry.problems)} problema(s) ({entry.input_hash})")
    return 0
