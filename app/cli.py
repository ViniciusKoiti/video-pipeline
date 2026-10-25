"""CLI `vp` (CLAUDE.md §10): ponto de entrada que monta o contexto e chama as etapas do pipeline.

Cada comando declara a etapa do roadmap que o implementa. Enquanto não houver handler registrado em
`HANDLERS`, o comando responde com a etapa pendente e sai com `EXIT_NOT_IMPLEMENTED`. O contexto só é
montado quando existe handler, e cada porta só quando usada.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from app.bootstrap import build_context
from app.commands import postiz, usage
from app.pipeline.bench import run_bench, summary
from app.pipeline.check import check_episode, episode_assets
from app.pipeline.excerpts import numbered_view
from app.pipeline.gates import (
    GATED_STEPS,
    GateError,
    GateStatus,
    gate_report,
    latest_check,
    missing_pieces,
    record_check,
    record_decision,
)
from app.pipeline.metrics import load_metrics, metrics_path, pending_lines, summary_line
from app.pipeline.music import load_music_catalog
from app.pipeline.numbers import (
    FORMAT_FILE,
    IMAGE_PLAN_FILE,
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
    EpisodeFormat,
    ScenesManifest,
    SourcesManifest,
    Status,
    Step,
)
from app.render.remotion import region_codes
from app.settings import CONFIG_FILE, speech_chars_per_second

EXIT_NOT_IMPLEMENTED = 3  # distinto de 1 (falha) e 2 (uso incorreto, argparse)

Handler = Callable[[argparse.Namespace, Context], int]


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    step: int  # etapa do roadmap (= issue #N) que implementa o comando
    takes_episode: bool = True
    add_arguments: Callable[[argparse.ArgumentParser], None] | None = None


def _bench_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--models", help="modelos de texto separados por vírgula (padrão: o configurado)")
    parser.add_argument("--runs", type=int, default=2, help="execuções por modelo (padrão: 2)")
    parser.add_argument("--skip-llm", action="store_true", help="não medir o LLM")
    parser.add_argument("--skip-tts", action="store_true", help="não medir o TTS")
    parser.add_argument(
        "--render", type=Path, metavar="DIR", help="pasta de episódio para medir o motor de render"
    )


def _new_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--topic", required=True, help="tema do episódio")
    parser.add_argument(
        "--format",
        choices=[f.value for f in EpisodeFormat],
        default=EpisodeFormat.ARCHIVAL_DOCUMENTARY.value,
        help="formato do episódio; decide o motor de render (ADR 001)",
    )


def _render_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--preview", action="store_true", help="prévia em 720p")


def _reopen_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--step", required=True, help="etapa aprovada a reabrir")
    parser.add_argument("--reason", required=True, help="motivo, registrado no review.json")


def _decision_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--step",
        required=True,
        choices=[s.value for s in GATED_STEPS],
        help="gate: sources (fontes e fichas), script (roteiro), assets (um ativo, com --asset) ou preview "
        "(o render mais acabado, com legenda e texto do post)",
    )
    parser.add_argument("--asset", help="id do ativo, na etapa assets")
    parser.add_argument("--reviewer", help="quem decide (padrão: git config user.name)")


def _approve_arguments(parser: argparse.ArgumentParser) -> None:
    _decision_arguments(parser)
    parser.add_argument("--notes", default="", help="observação registrada no review.json")
    parser.add_argument(
        "--sem-checagem",
        dest="skip_check",
        metavar="MOTIVO",
        help="aprova o gate 2 sem parecer do verificador; o motivo vai para o review.json",
    )


def _checagem_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("parecer", type=Path, help='JSON com "verdict" (approved | rejected) e "problems"')
    parser.add_argument("--reviewer", default="verificador", help="quem conferiu (padrão: verificador)")


def _reject_arguments(parser: argparse.ArgumentParser) -> None:
    _decision_arguments(parser)
    parser.add_argument("--reason", required=True, help="motivo, registrado no review.json")
    parser.add_argument("--changes", action="store_true", help="mudanças pedidas em vez de reprovação")


def _numeros_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--escrever", action="store_true", help="grava o bloco no outline.md e regrava o plano-imagens.md"
    )
    parser.add_argument(
        "--used-in-scenes",
        dest="used_in_scenes",
        action="store_true",
        help="acerta o used_in_scenes dos ativos ainda não aprovados (ativo aprovado não muda, §2.6)",
    )


COMMANDS: tuple[Command, ...] = (
    Command(
        "bench", "RAM, CPU, tok/s do modelo local, tempo de TTS", 5, takes_episode=False,
        add_arguments=_bench_arguments,
    ),
    Command("new", "cria data/episodes/<id>/ e o manifesto inicial", 12, add_arguments=_new_arguments),
    Command("sources", "busca, download e extração de texto -> sources.json", 26),
    Command("script", "roteiro com retrieval + validação de schema e de claims", 27),
    Command("scenes", "divisão em cenas + visual_need + search_query", 28),
    Command("assets", "busca visual em cascata, respeitando limites", 22),
    Command("gallery", "galeria HTML estática em 127.0.0.1", 23),
    Command("voice", "Kokoro por bloco + ffprobe -> voice/", 16),
    Command("subs", "legendas alinhadas -> captions.srt", 17),
    Command("render", "motor escolhido -> renders/", 13, add_arguments=_render_arguments),
    Command("export", "final.mp4 + srt + description.txt + credits.txt", 18),
    Command("approve", "registra aprovação humana em review.json", 12, add_arguments=_approve_arguments),
    Command("reject", "registra reprovação ou mudanças pedidas", 12, add_arguments=_reject_arguments),
    Command("status", "estados por etapa e pendências", 12),
    Command(
        "reopen", "reabre etapa aprovada para refazer (motivo no review.json)", 12,
        add_arguments=_reopen_arguments,
    ),
    Command("excerpts", "trechos numerados de cada fonte -> excerpts/<fonte>.md (ADR 009)", 48),
    Command("check", "valida fontes, fichas e cenas, escritas por agente ou à mão (ADR 009)", 48),
    Command(
        "checagem", "grava o parecer do verificador sobre fichas e roteiro -> checagem.json (gate 2)", 48,
        add_arguments=_checagem_arguments,
    ),
    Command(
        "numeros", "números do roteiro e comparação com o nicho -> bloco do outline.md (#170)", 170,
        add_arguments=_numeros_arguments,
    ),
)

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
    return 1 if any(not r.ok for r in [*report.llm, *report.tts, *report.render]) else 0


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


DECISION_LABELS = {
    Decision.APPROVED: "aprovado",
    Decision.REJECTED: "reprovado",
    Decision.CHANGES_REQUESTED: "mudanças pedidas",
}


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
            reviewer=args.reviewer or _git_user(),
            now=lambda: datetime.now().astimezone().replace(microsecond=0),
            asset_id=args.asset,
            notes=notes,
            skip_check=skip_check,
        )
    except (GateError, ManifestNotFound, EpisodeLocked) as error:
        print(f"vp {args.command}: {error}", file=sys.stderr)
        return 1
    target = entry.asset_id or entry.step.value
    print(f"{DECISION_LABELS[entry.decision]}: {target} por {entry.reviewer} ({entry.input_hash})")
    return 0


def _git_user() -> str:
    result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=False)
    if not result.stdout.strip():
        raise SystemExit("vp: informe --reviewer (git config user.name está vazio)")
    return result.stdout.strip()


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
    label = CHECK_LABELS[entry.verdict]
    print(f"checagem: {label} por {entry.reviewer}, {len(entry.problems)} problema(s) ({entry.input_hash})")
    return 0


CHECK_LABELS = {CheckVerdict.APPROVED: "aprovado", CheckVerdict.REJECTED: "reprovado"}


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
    label = DECISION_LABELS[entry.decision]
    return f"{kind:6}{target:32} {label:17} {entry.at:%Y-%m-%d %H:%M} {entry.reviewer} · {state}"


def _check_line(context: Context, episode_id: str) -> str:
    entry, valid = latest_check(context.store, episode_id)
    if entry is None:
        return f"{'parecer':6}{'verificador':32} sem parecer"
    state = "vale" if valid else "MUDOU depois do parecer"
    label = CHECK_LABELS[entry.verdict]
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
    if store.exists(episode_id, FORMAT_FILE):
        brief = store.read(episode_id, FORMAT_FILE, FormatBrief)
    try:
        numbers = script_numbers(scenes, assets, chars_per_second)
    except ValueError as error:
        print(f"vp numeros: {error} (rode vp check)", file=sys.stderr)
        return 1
    block = render_block(numbers, brief, chars_per_second)
    plan = render_image_plan(scenes, numbers, assets, chars_per_second)
    outline, plan_path = store.path(episode_id, "outline.md"), store.path(episode_id, IMAGE_PLAN_FILE)
    print(block)
    if not outline.is_file():
        print("outline.md: não existe", file=sys.stderr)
        return 1
    text = outline.read_text(encoding="utf-8")
    current = current_block(text)
    state = "em dia" if current == block else ("desatualizado" if current else "sem o bloco")
    plan_ok = plan_path.is_file() and plan_path.read_text(encoding="utf-8") == plan
    print(f"outline.md: {state}; {IMAGE_PLAN_FILE}: {'em dia' if plan_ok else 'diferente'}")
    with store.lock(episode_id):
        if args.escrever:
            targets = (
                ("outline.md", outline, replace_block(text, block)),
                (IMAGE_PLAN_FILE, plan_path, plan),
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
    for command in COMMANDS:
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
        if (folder / CONFIG_FILE).is_file():
            return folder
    raise SystemExit(f"vp: {CONFIG_FILE} não encontrado a partir de {start}")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handler = HANDLERS.get(args.command)
    if handler is not None:
        try:
            context = build_context(project_root(Path.cwd()))
        except (ValueError, OSError, SystemExit):
            if args.command not in ("postiz", "usage"):
                raise
            command_module = postiz if args.command == "postiz" else usage
            return command_module.report_error("Não foi possível carregar a configuração do projeto.")
        return handler(args, context)
    step = next(c.step for c in COMMANDS if c.name == args.command)
    print(f"vp {args.command}: ainda não implementado (etapa #{step} do roadmap).", file=sys.stderr)
    return EXIT_NOT_IMPLEMENTED
