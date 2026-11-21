"""`vp imagens`: imagem para lacuna pela tela do Gemini, no Chrome do dono (ADR 065; eram os scripts
`scripts/provisorio/imagens_navegador.py` e `fila_imagens.py`).

- `vp imagens plano <pedidos.json> --saida PASTA`: não abre navegador; mostra o que está pronto, o que falta e
  se a rodada passaria do teto.
- `vp imagens mapear`: abre o site do `[browser_image]` e lista o que cada seletor encontra, mais os botões e
  campos da página, para conferir e corrigir os seletores no `config/providers.toml`.
- `vp imagens gerar <pedidos.json> --saida PASTA [--rodada N] [--acima-do-teto]`: um pedido por conversa
  nova; grava cada imagem em PASTA com o id do pedido e uma linha no `registro.jsonl`.

O site, a porta do Chrome, a pausa entre pedidos e a espera vêm do `[browser_image]` do `providers.toml`;
o teto (12 por episódio, 2 por cena, §6) vem do `[limits]`. Gerar só com pedido do dono na sessão (§8). As
imagens ficam fora do episódio até o dono escolher (gate 3).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.errors import PipelineError
from app.pipeline.models.image_order import ImageOrder
from app.pipeline.ports import Context
from app.pipeline.visuals.image_queue import ImageQueueError, pending, read_orders
from app.pipeline.visuals.image_round import ceiling_problems, run_round
from app.providers.image_gen.base import PageMapper


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="imagens_command", required=True)
    plan = commands.add_parser("plano", help="o que está pronto e o que falta (não abre navegador)")
    generate = commands.add_parser("gerar", help="gera as imagens pendentes, uma por vez")
    for sub in (plan, generate):
        sub.add_argument("pedidos", type=Path)
        sub.add_argument("--saida", type=Path, required=True, help="pasta das imagens e do registro.jsonl")
    generate.add_argument(
        "--rodada", type=int, help="máximo de imagens nesta rodada (padrão: todas as pendentes)"
    )
    generate.add_argument(
        "--acima-do-teto",
        action="store_true",
        help="aceita passar do teto de 12 por episódio e 2 por cena (§6)",
    )
    commands.add_parser("mapear", help="lista o que cada seletor do site encontra na página")


def run(args: argparse.Namespace, context: Context) -> int:
    if args.imagens_command == "mapear":
        return _map(context)
    orders = read_orders(args.pedidos)
    batch = pending(orders, args.saida)
    limits = context.settings.limits
    if args.imagens_command == "gerar" and args.rodada is not None:
        batch = batch[: args.rodada]
    problems = ceiling_problems(
        orders,
        batch,
        args.saida,
        per_episode=limits.max_generated_images_per_episode,
        per_scene=limits.max_candidates_per_scene,
    )
    if args.imagens_command == "plano":
        return _plan(orders, batch, problems)
    return _generate(args, context, batch, problems)


def _plan(orders: list[ImageOrder], batch: list[ImageOrder], problems: list[str]) -> int:
    print(f"{len(orders)} pedidos; {len(orders) - len(batch)} prontos; {len(batch)} pendentes")
    for order in batch:
        print(f"  {order.id}  refs={len(order.refs)}  {order.prompt[:70]}")
    for problem in problems if batch else []:  # sem pendente, nada passa do teto nesta rodada
        print(f"acima do teto (§6): {problem}")
    return 0


def _generate(
    args: argparse.Namespace, context: Context, batch: list[ImageOrder], problems: list[str]
) -> int:
    if not batch:
        print("nada pendente")
        return 0
    if problems and not args.acima_do_teto:
        raise ImageQueueError(
            "acima do teto (§6): "
            + "; ".join(problems)
            + ". Corte o pedidos.json, use --rodada ou, por decisão sua, passe --acima-do-teto"
        )
    for problem in problems:
        print(f"aviso: acima do teto (§6), por --acima-do-teto: {problem}", file=sys.stderr)
    provider = context.image_gen
    try:
        made = run_round(
            provider, batch, args.saida, interval_s=context.settings.browser_image.interval_s, report=print
        )
    finally:
        provider.close()
    print(f"{made} de {len(batch)} imagens prontas em {args.saida}")
    return 0 if made == len(batch) else 1


def _map(context: Context) -> int:
    provider = context.image_gen
    try:
        if not isinstance(provider, PageMapper):
            raise PipelineError(f"o gerador {provider.info.name!r} não tem página para mapear")
        for line in provider.map_page():
            print(line)
    finally:
        provider.close()
    return 0
