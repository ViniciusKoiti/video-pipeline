"""Métricas de publicação aos 7 e 28 dias (§12), lidas à mão no YouTube Studio e no Instagram
(até `vp metricas`).

Uso:
  .venv/bin/python scripts/provisorio/metricas.py iniciar <id> --platform youtube --format longo
      [--channel "Cena e Conceito"] [--published-at 2026-10-20T22:00:00+00:00] [--post-id ...] [--url ...]
      [--series ...] [--duration-s 720] [--hypothesis "..."]
  .venv/bin/python scripts/provisorio/metricas.py ler <id> d7 [--read-at 2026-10-27] --views 1234 --likes 80
      --comments 12 --shares 3 --saves 5 --impressions 20000 --ctr 4.1 --duracao-media 312 --retencao-30s 71.5
      --inscritos 9 --origem "Navegação=42" --origem "Sugeridos=31" --pedido "duvida: ..." --nota "..."
      [--refazer]
  .venv/bin/python scripts/provisorio/metricas.py pendentes [--hoje 2026-10-23]
  .venv/bin/python scripts/provisorio/metricas.py tabela [--saida data/publicacoes/metricas.csv]

- `iniciar` cria o arquivo vazio. Data, canal e id do post vêm do registro do Postiz
  (`data/publicacoes/registro.jsonl`) quando o id é de um episódio agendado por ele; as flags completam ou
  sobrescrevem. Nunca sobrescreve um arquivo que já existe.
- O arquivo fica em `data/episodes/<id>/metrics.json`; sem pasta de episódio (clipe, story), em
  `data/publicacoes/metricas/<id>.json`.
- `ler` grava uma janela: o que não foi informado fica `null`, nunca zero. Recusa leitura antes de a janela
  fechar e segunda leitura da mesma janela sem `--refazer`.
- Não acessa rede.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.pipeline.metrics import (  # noqa: E402
    PUBLICATIONS_DIR,
    TABLE_FILE,
    all_metrics,
    load_metrics,
    metrics_path,
    record_reading,
    registry_path,
    save_metrics,
    scheduled_posts,
    summary_line,
    table_rows,
    write_table,
)
from app.pipeline.schemas import (  # noqa: E402
    WINDOW_DAYS,
    AudienceRequest,
    MetricsReading,
    PublicationMetrics,
    TrafficSource,
)
from app.settings import load_settings  # noqa: E402


def iniciar(args: argparse.Namespace, data_dir: Path) -> int:
    path = metrics_path(data_dir, args.id)
    if path.is_file():
        print(f"já existe: {path}", file=sys.stderr)
        return 1
    posts = [p for p in scheduled_posts(registry_path(data_dir)) if p.episode_id == args.id]
    post = posts[-1] if posts else None
    published_at = args.published_at or (post.scheduled_at if post else None)
    if published_at is None:
        print("sem --published-at e sem agendamento deste id no registro do Postiz", file=sys.stderr)
        return 1
    channel = args.channel or (post.channel if post else None)
    if not channel:
        print("sem --channel e sem canal no registro do Postiz", file=sys.stderr)
        return 1
    metrics = PublicationMetrics(
        id=args.id, platform=args.platform, channel=channel, format=args.format,
        published_at=published_at, url=args.url, post_id=args.post_id or (post.post_id if post else None),
        series=args.series, duration_s=args.duration_s, hypothesis=args.hypothesis,
    )
    save_metrics(path, metrics)
    origin = "registro do Postiz" if post and not args.published_at else "flags"
    print(f"criado {path} ({origin}); {summary_line(metrics, date.today())}")
    return 0


def _origem(text: str) -> TrafficSource:
    name, _, percent = text.rpartition("=")
    if not name:
        raise argparse.ArgumentTypeError(f"origem sem '=': {text!r} (ex.: 'Navegação=42')")
    return TrafficSource(name=name.strip(), percent=float(percent))


def _pedido(text: str, when: date) -> AudienceRequest:
    kind, sep, summary = text.partition(":")
    if not sep:
        raise argparse.ArgumentTypeError(f"pedido sem ':': {text!r} (ex.: 'duvida: como somar as horas')")
    return AudienceRequest(date=when, kind=kind.strip(), summary=summary.strip())


def ler(args: argparse.Namespace, data_dir: Path) -> int:
    path = metrics_path(data_dir, args.id)
    if not path.is_file():
        print(f"não existe: {path} (rode `iniciar` antes)", file=sys.stderr)
        return 1
    metrics = load_metrics(path)
    read_at = args.read_at or date.today()
    try:
        reading = MetricsReading(
            read_at=read_at, views=args.views, likes=args.likes, shares=args.shares, comments=args.comments,
            saves=args.saves, impressions=args.impressions, ctr_percent=args.ctr,
            avg_view_duration_s=args.duracao_media, retention_30s_percent=args.retencao_30s,
            subscribers_gained=args.inscritos, traffic_sources=[_origem(o) for o in args.origem],
            notes=args.nota or "",
        )
        updated = record_reading(metrics, args.janela, reading, replace=args.refazer)
        if args.pedido:
            requests = [*updated.requests, *(_pedido(p, read_at) for p in args.pedido)]
            updated = updated.model_copy(update={"requests": requests})
    except (ValueError, argparse.ArgumentTypeError) as error:
        print(f"recusado: {error}", file=sys.stderr)
        return 1
    save_metrics(path, updated)
    print(f"gravado {args.janela} em {path}; {summary_line(updated, date.today())}")
    return 0


def pendentes(args: argparse.Namespace, data_dir: Path) -> int:
    today = args.hoje or date.today()
    items = all_metrics(data_dir)
    if not items:
        print("nenhum metrics.json (rode `iniciar` para cada publicação)")
        return 0
    for _, metrics in items:
        print(f"{metrics.id:32} {summary_line(metrics, today)}")
    overdue = sum(len(m.pending(today)) for _, m in items)
    print(f"vencidas e não lidas: {overdue}")
    return 0


def tabela(args: argparse.Namespace, data_dir: Path) -> int:
    items = [metrics for _, metrics in all_metrics(data_dir)]
    rows = table_rows(items)
    out = args.saida or data_dir / PUBLICATIONS_DIR / TABLE_FILE
    write_table(out, rows)
    print(f"{out}: {len(items)} publicação(ões), {len(rows)} linha(s)")
    return 0


def main() -> int:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("iniciar", help="cria o metrics.json vazio de uma publicação")
    p.add_argument("id")
    p.add_argument("--platform", required=True, choices=["youtube", "instagram", "tiktok"])
    p.add_argument("--format", required=True, choices=["longo", "reel", "clipe", "story"])
    p.add_argument("--channel")
    p.add_argument("--published-at", type=datetime.fromisoformat, help="ISO com fuso; padrão: o registro")
    p.add_argument("--post-id")
    p.add_argument("--url")
    p.add_argument("--series")
    p.add_argument("--duration-s", type=float)
    p.add_argument("--hypothesis", help="hipótese de forma (#122): o que se espera ver e em que medida")
    p.set_defaults(run=iniciar)

    p = sub.add_parser("ler", help="grava a leitura de uma janela")
    p.add_argument("id")
    p.add_argument("janela", choices=list(WINDOW_DAYS))
    p.add_argument("--read-at", type=date.fromisoformat, help="padrão: hoje")
    for name in ("views", "likes", "shares", "comments", "saves", "impressions", "inscritos"):
        p.add_argument(f"--{name}", type=int)
    p.add_argument("--ctr", type=float, help="cliques por impressão, em %%")
    p.add_argument("--duracao-media", type=float, help="duração média da visualização, em segundos")
    p.add_argument("--retencao-30s", type=float, help="%% do público que passa dos 30 s iniciais")
    p.add_argument("--origem", action="append", default=[], help="'Nome=percentual'; repetível")
    p.add_argument("--pedido", action="append", default=[],
                   help="'tipo: resumo' (planilha, modelo, duvida, outro)")
    p.add_argument("--nota")
    p.add_argument("--refazer", action="store_true", help="substitui uma leitura já gravada")
    p.set_defaults(run=ler)

    p = sub.add_parser("pendentes", help="janelas vencidas e por vencer, de todas as publicações")
    p.add_argument("--hoje", type=date.fromisoformat)
    p.set_defaults(run=pendentes)

    p = sub.add_parser("tabela", help="CSV consolidado (uma linha por janela)")
    p.add_argument("--saida", type=Path)
    p.set_defaults(run=tabela)

    args = parser.parse_args()
    settings = load_settings(ROOT)
    return args.run(args, settings.data_dir)


if __name__ == "__main__":
    raise SystemExit(main())
