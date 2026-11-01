"""Argumentos de `vp metricas`: os tipos de cada opção, validados pelo próprio argparse."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from app.pipeline.constants.schemas_constants import SchemasConstants


def _origin(text: str) -> tuple[str, float]:
    name, _, percent = text.rpartition("=")
    if not name:
        raise argparse.ArgumentTypeError(f"origem sem '=': {text!r} (ex.: 'Navegação=42')")
    try:
        return name.strip(), float(percent)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"percentual inválido em {text!r}") from error


def _request(text: str) -> tuple[str, str]:
    kind, separator, summary = text.partition(":")
    if not separator:
        raise argparse.ArgumentTypeError(f"pedido sem ':': {text!r} (ex.: 'duvida: como somar as horas')")
    return kind.strip(), summary.strip()


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="metricas_command", required=True)
    start = commands.add_parser("iniciar", help="cria o metrics.json vazio de uma publicação")
    start.add_argument("publication_id", metavar="id")
    start.add_argument("--platform", required=True, choices=["youtube", "instagram", "tiktok"])
    start.add_argument("--format", required=True, choices=["longo", "reel", "clipe", "story"])
    start.add_argument("--channel")
    start.add_argument("--published-at", type=datetime.fromisoformat, help="ISO com fuso; padrão: o registro")
    start.add_argument("--post-id")
    start.add_argument("--url")
    start.add_argument("--series")
    start.add_argument("--duration-s", type=float)
    start.add_argument("--hypothesis", help="hipótese de forma (#122): o que se espera ver e em que medida")
    read = commands.add_parser("ler", help="grava a leitura de uma janela")
    read.add_argument("publication_id", metavar="id")
    read.add_argument("janela", choices=list(SchemasConstants.WINDOW_DAYS))
    read.add_argument("--read-at", type=date.fromisoformat, help="padrão: hoje")
    for name in ("views", "likes", "shares", "comments", "saves", "impressions", "inscritos"):
        read.add_argument(f"--{name}", type=int)
    read.add_argument("--ctr", type=float, help="cliques por impressão, em %%")
    read.add_argument("--duracao-media", type=float, help="duração média da visualização, em segundos")
    read.add_argument("--retencao-30s", type=float, help="%% do público que passa dos 30 s iniciais")
    read.add_argument(
        "--origem", action="append", default=[], type=_origin, help="'Nome=percentual'; repetível"
    )
    read.add_argument(
        "--pedido",
        action="append",
        default=[],
        type=_request,
        help="'tipo: resumo' (planilha, modelo, duvida, outro)",
    )
    read.add_argument("--nota")
    read.add_argument("--refazer", action="store_true", help="substitui uma leitura já gravada")
    pending = commands.add_parser("pendentes", help="janelas vencidas e por vencer, de todas as publicações")
    pending.add_argument("--hoje", type=date.fromisoformat)
    table = commands.add_parser("tabela", help="CSV consolidado (uma linha por janela)")
    table.add_argument("--saida", type=Path)
