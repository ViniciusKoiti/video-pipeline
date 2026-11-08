"""`vp status <id>`: onde está cada gate de um episódio (CLAUDE.md §5).

Uma linha por gate e por ativo (decisão, quem, quando, e se ela ainda vale para o conteúdo de hoje), o parecer
do verificador, a conferência do render carimbável (§4), as janelas de métricas vencidas (§12) e a lista de
pendências, com a legenda que falta no vertical, as falas que ficaram para trás (ADR 052) e o render com
problema. Só lê.
"""

from __future__ import annotations

import argparse
from datetime import date

from app.commands.constants.cli_constants import CliConstants
from app.pipeline.gates import GateStatus, gate_report, latest_check
from app.pipeline.metrics import load_metrics, metrics_path, pending_lines, summary_line
from app.pipeline.pending import pending_pieces
from app.pipeline.ports import Context
from app.pipeline.render_checks import status_line as render_status_line
from app.pipeline.schemas import Decision, Step


def run(args: argparse.Namespace, context: Context) -> int:
    rows = gate_report(context.store, context.review, args.episode_id)
    for row in rows:
        print(_status_line(row))
        if row.step is Step.SCRIPT:
            print(_check_line(context, args.episode_id))
    if (render := render_status_line(context.store, args.episode_id)) is not None:
        print(render)
    pending = [row.asset_id or row.step.value for row in rows if _pending(row)]
    pending += pending_pieces(context.store, args.episode_id)
    pending += _metrics_status(context, args.episode_id)
    print("pendências: " + (", ".join(pending) if pending else "nenhuma"))
    return 0


def _metrics_status(context: Context, episode_id: str) -> list[str]:
    """Depois de publicado (§12): mostra as janelas de 7 e 28 dias e devolve as vencidas sem leitura."""
    path = metrics_path(context.settings.data_dir, episode_id)
    if not path.is_file():
        return []
    try:
        metrics = load_metrics(path)
    except ValueError:
        return ["metrics.json inválido (ver vp check)"]
    print(f"{'métricas':38} {summary_line(metrics, date.today())}")
    return pending_lines(metrics, date.today())


def _status_line(row: GateStatus) -> str:
    kind, target = ("ativo", row.asset_id) if row.asset_id else ("gate", row.step.value)
    if row.entry is None:
        return f"{kind:6}{target:32} sem decisão"
    if row.current_hash is None:
        state = "arquivo removido"
    else:
        state = "vale" if row.valid else "MUDOU depois da decisão"
    entry = row.entry
    label = CliConstants.DECISION_LABELS[entry.decision]
    return f"{kind:6}{target:32} {label:17} {entry.at:%Y-%m-%d %H:%M} {entry.reviewer} · {state}"


def _check_line(context: Context, episode_id: str) -> str:
    entry, valid = latest_check(context.store, episode_id)
    if entry is None:
        return f"{'parecer':6}{'verificador':32} sem parecer"
    state = "vale" if valid else "MUDOU depois do parecer"
    label = CliConstants.CHECK_LABELS[entry.verdict]
    return f"{'parecer':6}{'verificador':32} {label:17} {entry.at:%Y-%m-%d %H:%M} {entry.reviewer} · {state}"


def _pending(row: GateStatus) -> bool:
    """Gate sem aprovação que valha; ativo rejeitado e removido não é pendência."""
    if row.asset_id and row.current_hash is None:
        return False
    return not (row.entry is not None and row.entry.decision is Decision.APPROVED and row.valid)
