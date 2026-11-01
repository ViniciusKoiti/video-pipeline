"""CLI `vp` (CLAUDE.md §10): ponto de entrada que monta o contexto e chama as etapas do pipeline.

Cada comando declara a etapa do roadmap que o implementa. Enquanto não houver handler registrado em
`HANDLERS`, o comando responde com a etapa pendente e sai com `EXIT_NOT_IMPLEMENTED`. O contexto só é
montado quando existe handler, e cada porta só quando usada.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from datetime import date, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from app.bootstrap import build_context
from app.commands import postiz, usage
from app.commands.constants.cli_constants import CliConstants
from app.commands.models.command import Command as Command
from app.pipeline.bench import run_bench, summary
from app.pipeline.check import check_episode, episode_assets
from app.pipeline.constants.numbers_constants import NumbersConstants
from app.pipeline.excerpts import numbered_view
from app.pipeline.gates import (
    GateError,
    GateStatus,
    gate_report,
    latest_check,
    missing_pieces,
    record_check,
    record_decision,
)
from app.pipeline.medicao import medicao_problems
from app.pipeline.metrics import load_metrics, metrics_path, pending_lines, summary_line
from app.pipeline.music import load_music_catalog
from app.pipeline.numbers import (
    FormatBrief,
    current_block,
    render_block,
    render_image_plan,
    replace_block,
    script_numbers,
    used_in_scenes_mismatches,
)
from app.pipeline.ports import Context, EpisodeLocked, ManifestNotFound
from app.pipeline.schemas import (
    CheckVerdict,
    Decision,
    ScenesManifest,
    SourcesManifest,
    Status,
    Step,
)
from app.pipeline.translation import translation_problems
from app.render.remotion import region_codes
from app.settings import read_dotenv, speech_chars_per_second
from app.settings.constants.settings_constants import SettingsConstants

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


def _approve(args: argparse.Namespace, context: Context) -> int:
    return _decide(args, context, Decision.APPROVED, args.notes, skip_check=args.skip_check)


def _reject(args: argparse.Namespace, context: Context) -> int:
    decision = Decision.CHANGES_REQUESTED if args.changes else Decision.REJECTED
    return _decide(args, context, decision, args.reason)


def _decide(
    args: argparse.Namespace, context: Context, decision: Decision, notes: str, skip_check: str | None = None
) -> int:
    try:
        entry = record_decision(
            context.store,
            context.review,
            args.episode_id,
            Step(args.step),
            decision,
            reviewer=args.reviewer or _default_reviewer(),
            now=lambda: datetime.now().astimezone().replace(microsecond=0),
            asset_id=args.asset,
            notes=notes,
            skip_check=skip_check,
        )
    except (GateError, ManifestNotFound, EpisodeLocked) as error:
        print(f"vp {args.command}: {error}", file=sys.stderr)
        return 1
    target = entry.asset_id or entry.step.value
    print(
        f"{CliConstants.DECISION_LABELS[entry.decision]}: {target} por {entry.reviewer} ({entry.input_hash})"
    )
    return 0


def _default_reviewer() -> str:
    """`VP_REVIEWER` do ambiente; senão o nome do git, com aviso, porque ele vai assinar a decisão do gate."""
    root = project_root(Path.cwd())
    name = (os.environ.get("VP_REVIEWER") or read_dotenv(root / ".env").get("VP_REVIEWER", "")).strip()
    if name:
        return name
    name = _git_user()
    print(
        f"vp: decisão assinada como '{name}' (git config user.name); "
        "use --reviewer ou VP_REVIEWER para assinar com o seu nome",
        file=sys.stderr,
    )
    return name


def _git_user() -> str:
    result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=False)
    if not result.stdout.strip():
        raise SystemExit("vp: informe --reviewer (git config user.name está vazio)")
    return result.stdout.strip()


def _medicao(args: argparse.Namespace, context: Context) -> int:
    problems, warnings = medicao_problems(context.store, args.episode_id)
    for problem in problems:
        print(f"- {problem}")
    for warning in warnings:
        print(f"- aviso: {warning}")
    print("resultado: " + (f"{len(problems)} problema(s)" if problems else "sem problemas"))
    return 1 if problems else 0


def _traducao(args: argparse.Namespace, context: Context) -> int:
    problems = translation_problems(context.store, args.episode_id)
    for problem in problems:
        print(f"- {problem}")
    print("resultado: " + (f"{len(problems)} problema(s)" if problems else "sem problemas"))
    return 1 if problems else 0


def _checagem(args: argparse.Namespace, context: Context) -> int:
    try:
        report = json.loads(args.parecer.read_text(encoding="utf-8"))
        verdict = CheckVerdict(report["verdict"])
        problems = report.get("problems", [])
        entry = record_check(
            context.store, args.episode_id, verdict, problems, reviewer=args.reviewer,
            now=lambda: datetime.now().astimezone().replace(microsecond=0),
        )
    except (OSError, ValueError, KeyError, TypeError, GateError, EpisodeLocked) as error:
        print(f"vp checagem: parecer inválido ou episódio sem roteiro ({error})", file=sys.stderr)
        return 1
    label = CliConstants.CHECK_LABELS[entry.verdict]
    print(f"checagem: {label} por {entry.reviewer}, {len(entry.problems)} problema(s) ({entry.input_hash})")
    return 0


def _status(args: argparse.Namespace, context: Context) -> int:
    rows = gate_report(context.store, context.review, args.episode_id)
    for row in rows:
        print(_status_line(row))
        if row.step is Step.SCRIPT:
            print(_check_line(context, args.episode_id))
    pending = [row.asset_id or row.step.value for row in rows if _pending(row)]
    pending += missing_pieces(context.store, args.episode_id)
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
def _write_if_changed(path: Path, text: str) -> bool:
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def _numeros(args: argparse.Namespace, context: Context) -> int:
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


HANDLERS: dict[str, Handler] = {
    "bench": _bench,
    "excerpts": _excerpts,
    "check": _check,
    "approve": _approve,
    "reject": _reject,
    "status": _status,
    "checagem": _checagem,
    "traducao": _traducao,
    "medicao": _medicao,
    "numeros": _numeros,
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
    usage.add_arguments(
        subparsers.add_parser("usage", help="consumo e orçamento dos agentes em SQLite local")
    )
    return parser


def project_root(start: Path) -> Path:
    """Primeira pasta, subindo a partir de `start`, que tem `config/providers.toml`."""
    for folder in (start, *start.parents):
        if (folder / SettingsConstants.CONFIG_FILE).is_file():
            return folder
    raise SystemExit(f"vp: {SettingsConstants.CONFIG_FILE} não encontrado a partir de {start}")


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
        return handler(args, context)
    step = next(c.step for c in CliConstants.COMMANDS if c.name == args.command)
    print(f"vp {args.command}: ainda não implementado (etapa #{step} do roadmap).", file=sys.stderr)
    return CliConstants.EXIT_NOT_IMPLEMENTED
