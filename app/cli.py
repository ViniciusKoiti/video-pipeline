"""CLI `vp` (CLAUDE.md §10): ponto de entrada que monta o contexto e chama as etapas do pipeline.

Cada comando declara a etapa do roadmap que o implementa. Enquanto não houver handler registrado em
`HANDLERS`, o comando responde com a etapa pendente e sai com `EXIT_NOT_IMPLEMENTED`. O contexto só é
montado quando existe handler, e cada porta só quando usada.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from app.bootstrap import build_context
from app.pipeline.bench import run_bench, summary
from app.pipeline.check import check_episode
from app.pipeline.excerpts import numbered_view
from app.pipeline.ports import Context
from app.pipeline.schemas import EpisodeFormat, SourcesManifest
from app.settings import CONFIG_FILE

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


def _approve_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--step", required=True, help="etapa a aprovar")


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
    Command("status", "estados por etapa e pendências", 12),
    Command(
        "reopen", "reabre etapa aprovada para refazer (motivo no review.json)", 12,
        add_arguments=_reopen_arguments,
    ),
    Command("excerpts", "trechos numerados de cada fonte -> excerpts/<fonte>.md (ADR 009)", 48),
    Command("check", "valida fontes, fichas e cenas, escritas por agente ou à mão (ADR 009)", 48),
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
    report = check_episode(context.store, args.episode_id)
    for line in report.checked:
        print(f"ok      {line}")
    for line in report.warnings:
        print(f"alerta  {line}")
    for line in report.errors:
        print(f"erro    {line}")
    print("resultado: " + ("sem erros" if report.ok else f"{len(report.errors)} erro(s)"))
    return 0 if report.ok else 1


# Preenchido conforme as etapas forem implementadas: nome do comando -> handler.
HANDLERS: dict[str, Handler] = {"bench": _bench, "excerpts": _excerpts, "check": _check}


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
        return handler(args, build_context(project_root(Path.cwd())))
    step = next(c.step for c in COMMANDS if c.name == args.command)
    print(f"vp {args.command}: ainda não implementado (etapa #{step} do roadmap).", file=sys.stderr)
    return EXIT_NOT_IMPLEMENTED
