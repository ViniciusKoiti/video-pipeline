"""CLI `vp` (CLAUDE.md §10): ponto de entrada que monta o contexto e chama as etapas do pipeline.

Cada comando declara a etapa do roadmap que o implementa. Enquanto não houver handler registrado em
`HANDLERS`, o comando responde com a etapa pendente e sai com `EXIT_NOT_IMPLEMENTED`. O contexto só é
montado quando existe handler, e cada porta só quando usada.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from datetime import date, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from app.bootstrap import build_context
from app.commands import (
    assets,
    briefs,
    conferences,
    decisions,
    music,
    numeros,
    postiz,
    reopen,
    sources,
    usage,
)
from app.commands.constants.cli_constants import CliConstants
from app.commands.errors import run
from app.commands.models.command import Command as Command
from app.commands.project_root import project_root
from app.pipeline.bench import run_bench, summary
from app.pipeline.check import check_episode
from app.pipeline.excerpts import numbered_view
from app.pipeline.gates import (
    GateStatus,
    gate_report,
    latest_check,
)
from app.pipeline.metrics import load_metrics, metrics_path, pending_lines, summary_line
from app.pipeline.music import load_music_catalog
from app.pipeline.pending import pending_pieces
from app.pipeline.ports import Context
from app.pipeline.schemas import (
    Decision,
    SourcesManifest,
    Step,
)
from app.render.remotion import region_codes
from app.settings import speech_chars_per_second

Handler = Callable[[argparse.Namespace, Context], int]


def _bench(args: argparse.Namespace, context: Context) -> int:
    models = [m.strip() for m in args.models.split(",")] if args.models else [None]
    report, path = run_bench(
        context,
        models=models,
        runs=args.runs,
        now=lambda: datetime.now().astimezone(),
        include_llm=not args.skip_llm,
        include_tts=not args.skip_tts,
        render_dir=args.render,
        progress=lambda message: print(message, file=sys.stderr, flush=True),
    )
    print("\n".join(summary(report)))
    print(f"resultado: {path}")
    return 1 if any(not r.ok for runs in (report.llm, report.tts, report.render) for r in runs) else 0


def _excerpts(args: argparse.Namespace, context: Context) -> int:
    store = context.store
    sources = store.read(args.episode_id, "sources.json", SourcesManifest)
    for source in sources.sources:
        text = store.path(args.episode_id, source.local_path).read_text(encoding="utf-8")
        out = store.path(args.episode_id, f"excerpts/{source.id}.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(numbered_view(source, text), encoding="utf-8")
        print(out)
    return 0


def _check(args: argparse.Namespace, context: Context) -> int:
    report = check_episode(
        context.store, args.episode_id, region_codes=region_codes(),
        chars_per_second=speech_chars_per_second(context.settings), today=date.today(),
        music_catalog=load_music_catalog(context.settings.data_dir),
    )
    for line in report.checked:
        print(f"ok      {line}")
    for line in report.warnings:
        print(f"alerta  {line}")
    for line in report.errors:
        print(f"erro    {line}")
    print("resultado: " + ("sem erros" if report.ok else f"{len(report.errors)} erro(s)"))
    return 0 if report.ok else 1


def _status(args: argparse.Namespace, context: Context) -> int:
    rows = gate_report(context.store, context.review, args.episode_id)
    for row in rows:
        print(_status_line(row))
        if row.step is Step.SCRIPT:
            print(_check_line(context, args.episode_id))
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


# Preenchido conforme as etapas forem implementadas: nome do comando -> handler.
HANDLERS: dict[str, Handler] = {
    "bench": _bench,
    "excerpts": _excerpts,
    "check": _check,
    "approve": decisions.approve,
    "reject": decisions.reject,
    "reopen": reopen.run,
    "status": _status,
    "checagem": decisions.checagem,
    "traducao": conferences.traducao,
    "medicao": conferences.medicao,
    "numeros": numeros.run,
    "sources": sources.run,
    "assets": assets.run,
    "briefs": briefs.run,
    "music": music.run,
    "postiz": postiz.run,
    "usage": usage.run,
}


def _package_version() -> str:
    try:
        return version("video-pipeline")
    except PackageNotFoundError:
        return "desconhecida"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vp",
        description="video-pipeline: vídeos narrados a partir de fontes verificáveis.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_package_version()}")
    subparsers = parser.add_subparsers(dest="command", metavar="<comando>", required=True)
    for command in CliConstants.COMMANDS:
        sub = subparsers.add_parser(command.name, help=command.help, description=command.help)
        if command.takes_episode:
            sub.add_argument("episode_id", metavar="id", help="identificador do episódio")
        if command.add_arguments is not None:
            command.add_arguments(sub)
    postiz.add_arguments(subparsers.add_parser("postiz", help="canais, mídia e agendamentos em JSON"))
    assets.add_arguments(subparsers.add_parser("assets", help="busca e baixa ativos visuais (ADR 044)"))
    briefs.add_arguments(subparsers.add_parser("briefs", help="resumo do radar e perfil do nicho (ADR 047)"))
    music.add_arguments(subparsers.add_parser("music", help="catálogo de música de fundo (ADR 030)"))
    sources.add_arguments(subparsers.add_parser("sources", help="registra uma fonte (ADR 043)"))
    usage.add_arguments(
        subparsers.add_parser("usage", help="consumo e orçamento dos agentes em SQLite local")
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = HANDLERS.get(args.command)
    if handler is not None:
        try:
            context = build_context(project_root(Path.cwd()))
        except (ValueError, OSError, SystemExit):
            if args.command not in ("postiz", "usage"):
                raise
            report_error = postiz.report_error if args.command == "postiz" else usage.report_error
            return report_error("Não foi possível carregar a configuração do projeto.")
        return run(f"vp {args.command}", lambda: handler(args, context))
    step = next(c.step for c in CliConstants.COMMANDS if c.name == args.command)
    print(f"vp {args.command}: ainda não implementado (etapa #{step} do roadmap).", file=sys.stderr)
    return CliConstants.EXIT_NOT_IMPLEMENTED
