"""`vp metricas`: métricas de publicação aos 7 e 28 dias (§12), lidas à mão no Studio e no Instagram.

- `vp metricas iniciar <id> --platform youtube --format longo|short|reel|clipe|story [--channel]
  [--published-at ISO] [--post-id] [--url] [--series] [--duration-s N] [--hypothesis "..."]`: cria o arquivo
  vazio. Data, canal e id do post vêm do registro do Postiz (`data/publicacoes/registro.jsonl`) quando o id é
  de um episódio agendado por ele; as opções completam ou sobrescrevem. Nunca sobrescreve um arquivo que já
  existe. É o único jeito certo de criar o arquivo: um `metrics.json` escrito à mão fora do contrato aparece
  em `pendentes` e `tabela` como INVÁLIDO (saída 1) sem esconder as outras publicações.
- `vp metricas ler <id> d7|d28 [--read-at AAAA-MM-DD] --views N ... [--origem "Nome=42"]
  [--pedido "tipo: resumo"] [--nota] [--refazer]`: grava uma janela; o que não foi informado fica `null`,
  nunca zero. Recusa leitura antes de a janela fechar e segunda leitura da mesma janela sem `--refazer`.
- `vp metricas pendentes [--hoje AAAA-MM-DD]`: janelas vencidas e por vencer de todas as publicações.
- `vp metricas tabela [--saida arquivo.csv]`: CSV consolidado, uma linha por janela.

O arquivo fica em `data/episodes/<id>/metrics.json`; sem pasta de episódio (clipe, story), em
`data/publicacoes/metricas/<id>.json`. Não acessa rede.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from app.commands.metricas_arguments import add_arguments as add_arguments
from app.pipeline.constants.metrics_constants import MetricsConstants
from app.pipeline.metrics import (
    MetricsError,
    all_metrics,
    invalid_metrics,
    load_metrics,
    metrics_path,
    publication_id,
    record_reading,
    registry_path,
    save_metrics,
    scheduled_posts,
    summary_line,
    table_rows,
    write_table,
)
from app.pipeline.ports import Context
from app.pipeline.schemas import AudienceRequest, MetricsReading, PublicationMetrics, TrafficSource


def run(args: argparse.Namespace, context: Context) -> int:
    handler = {"iniciar": _start, "ler": _read, "pendentes": _pending, "tabela": _table}
    return handler[args.metricas_command](args, context.settings.data_dir)


def _start(args: argparse.Namespace, data_dir: Path) -> int:
    path = metrics_path(data_dir, args.publication_id)
    if path.is_file():
        raise MetricsError(f"já existe: {path}")
    posts = [p for p in scheduled_posts(registry_path(data_dir)) if p.episode_id == args.publication_id]
    post = posts[-1] if posts else None
    published_at = args.published_at or (post.scheduled_at if post else None)
    if published_at is None:
        raise MetricsError("sem --published-at e sem agendamento deste id no registro do Postiz")
    channel = args.channel or (post.channel if post else None)
    if not channel:
        raise MetricsError("sem --channel e sem canal no registro do Postiz")
    metrics = PublicationMetrics(
        id=args.publication_id,
        platform=args.platform,
        channel=channel,
        format=args.format,
        published_at=published_at,
        url=args.url,
        post_id=args.post_id or (post.post_id if post else None),
        series=args.series,
        duration_s=args.duration_s,
        hypothesis=args.hypothesis,
    )
    save_metrics(path, metrics)
    origin = "registro do Postiz" if post and not args.published_at else "flags"
    print(f"criado {path} ({origin}); {summary_line(metrics, date.today())}")
    return 0


def _reading(args: argparse.Namespace, read_at: date) -> MetricsReading:
    return MetricsReading(
        read_at=read_at,
        views=args.views,
        likes=args.likes,
        shares=args.shares,
        comments=args.comments,
        saves=args.saves,
        impressions=args.impressions,
        ctr_percent=args.ctr,
        avg_view_duration_s=args.duracao_media,
        retention_30s_percent=args.retencao_30s,
        subscribers_gained=args.inscritos,
        traffic_sources=[TrafficSource(name=name, percent=percent) for name, percent in args.origem],
        notes=args.nota or "",
    )


def _read(args: argparse.Namespace, data_dir: Path) -> int:
    path = metrics_path(data_dir, args.publication_id)
    if not path.is_file():
        raise MetricsError(f"não existe: {path} (rode `vp metricas iniciar` antes)")
    metrics = load_metrics(path)
    read_at = args.read_at or date.today()
    try:
        updated = record_reading(metrics, args.janela, _reading(args, read_at), replace=args.refazer)
    except ValidationError as error:  # janela que ainda não fechou, número fora da faixa
        reasons = "; ".join(e["msg"].removeprefix("Value error, ") for e in error.errors())
        raise MetricsError(f"recusado: {reasons}") from error
    if args.pedido:
        asked = [AudienceRequest(date=read_at, kind=kind, summary=text) for kind, text in args.pedido]
        updated = updated.model_copy(update={"requests": [*updated.requests, *asked]})
    save_metrics(path, updated)
    print(f"gravado {args.janela} em {path}; {summary_line(updated, date.today())}")
    return 0


def _pending(args: argparse.Namespace, data_dir: Path) -> int:
    today = args.hoje or date.today()
    items = all_metrics(data_dir)
    invalid = invalid_metrics(data_dir)
    if not items and not invalid:
        print("nenhum metrics.json (rode `vp metricas iniciar` para cada publicação)")
        return 0
    for _, metrics in items:
        print(f"{metrics.id:32} {summary_line(metrics, today)}")
    _print_invalid(invalid)
    print(f"vencidas e não lidas: {sum(len(m.pending(today)) for _, m in items)}")
    return 1 if invalid else 0


def _table(args: argparse.Namespace, data_dir: Path) -> int:
    items = [metrics for _, metrics in all_metrics(data_dir)]
    invalid = invalid_metrics(data_dir)
    rows = table_rows(items)
    out = args.saida or data_dir / MetricsConstants.PUBLICATIONS_DIR / MetricsConstants.TABLE_FILE
    write_table(out, rows)
    print(f"{out}: {len(items)} publicação(ões), {len(rows)} linha(s)")
    _print_invalid(invalid)
    return 1 if invalid else 0


def _print_invalid(invalid: list[tuple[Path, str]]) -> None:
    """Um arquivo fora do contrato fica visível e fora da conta; o comando sai com 1 para ninguém o perder."""
    for path, reason in invalid:
        hint = "corrija o arquivo ou refaça com `vp metricas iniciar`"
        print(f"{publication_id(path):32} INVÁLIDO ({reason}); {hint}")
