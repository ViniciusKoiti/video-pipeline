"""Métricas de publicação (§12): onde fica o `metrics.json`, o que o registro do Postiz já sabe de cada
agendamento, o que está vencido e a tabela consolidada. Os números entram à mão: sem API do YouTube nesta
fase. Contrato em `PublicationMetrics` (schemas.py)."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.pipeline.schemas import (
    METRICS_FILE,
    READING_NUMBERS,
    WINDOW_DAYS,
    MetricsReading,
    PublicationMetrics,
)

EPISODES_DIR = "episodes"
PUBLICATIONS_DIR = "publicacoes"
REGISTRY_FILE = "registro.jsonl"
METRICS_DIR = "metricas"
TABLE_FILE = "metricas.csv"


@dataclass(frozen=True)
class ScheduledPost:
    """Um agendamento do registro: o `pacote` e o `agendado` com o mesmo payload."""

    episode_id: str | None
    channel: str
    integration_id: str
    scheduled_at: datetime
    post_id: str | None
    media: str | None


def registry_path(data_dir: Path) -> Path:
    return data_dir / PUBLICATIONS_DIR / REGISTRY_FILE


def scheduled_posts(registry: Path) -> list[ScheduledPost]:
    """Lê `registro.jsonl` (ADR 025) e devolve um item por post agendado, na ordem do registro."""
    if not registry.is_file():
        return []
    rows = [json.loads(line) for line in registry.read_text(encoding="utf-8").splitlines() if line.strip()]
    packages: dict[str, dict[str, Any]] = {}  # payload -> último pacote com esse conteúdo
    result: list[ScheduledPost] = []
    for row in rows:
        if row.get("event") == "pacote":
            packages[row.get("payload", "")] = row
        elif row.get("event") == "agendado":
            package = packages.get(row.get("payload", ""))
            if package is None:
                continue
            scheduled = row.get("posts") or []
            episode_id = (package.get("evidencia") or {}).get("episodio")
            for post in (package.get("o_que") or {}).get("posts", []):
                integration = post.get("canal_id", "")
                post_id = next(
                    (p.get("postId") for p in scheduled if p.get("integration") == integration), None
                )
                media = [m.get("arquivo") for m in post.get("midia", []) if m.get("arquivo")]
                result.append(
                    ScheduledPost(
                        episode_id=episode_id,
                        channel=post.get("canal", ""),
                        integration_id=integration,
                        scheduled_at=datetime.fromisoformat(row["data"]),
                        post_id=post_id,
                        media=media[0] if media else None,
                    )
                )
    return result


def metrics_path(data_dir: Path, publication_id: str) -> Path:
    """Na pasta do episódio quando ela existe; senão em `data/publicacoes/metricas/<id>.json`."""
    episode_dir = data_dir / EPISODES_DIR / publication_id
    if episode_dir.is_dir():
        return episode_dir / METRICS_FILE
    return data_dir / PUBLICATIONS_DIR / METRICS_DIR / f"{publication_id}.json"


def load_metrics(path: Path) -> PublicationMetrics:
    return PublicationMetrics.model_validate_json(path.read_text(encoding="utf-8"))


def save_metrics(path: Path, metrics: PublicationMetrics) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(metrics.model_dump_json(indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)  # atômico: o arquivo nunca fica pela metade


def all_metrics(data_dir: Path) -> list[tuple[Path, PublicationMetrics]]:
    """Todos os arquivos de métricas, dos episódios e das publicações sem episódio, por id."""
    paths = list((data_dir / EPISODES_DIR).glob(f"*/{METRICS_FILE}"))
    paths += list((data_dir / PUBLICATIONS_DIR / METRICS_DIR).glob("*.json"))
    items = [(path, load_metrics(path)) for path in paths]
    return sorted(items, key=lambda item: item[1].id)


def record_reading(
    metrics: PublicationMetrics, window: str, reading: MetricsReading, *, replace: bool = False
) -> PublicationMetrics:
    """Uma janela é lida uma vez; `replace` refaz uma leitura errada. Valida de novo o arquivo inteiro."""
    if window in metrics.readings and not replace:
        done = metrics.readings[window].read_at
        raise ValueError(f"{window} já lida em {done:%Y-%m-%d}; use --refazer para substituir")
    data = metrics.model_dump(mode="json")
    data["readings"] = {**data["readings"], window: reading.model_dump(mode="json")}
    return PublicationMetrics.model_validate(data)


def pending_lines(metrics: PublicationMetrics, today: date) -> list[str]:
    """Para as pendências do `vp status`: janelas fechadas e não lidas."""
    return [f"métricas {w} (venceu {metrics.due_date(w):%Y-%m-%d})" for w in metrics.pending(today)]


def summary_line(metrics: PublicationMetrics, today: date) -> str:
    parts = [f"publicado {metrics.published_at:%Y-%m-%d} ({metrics.platform}, {metrics.channel})"]
    for window in WINDOW_DAYS:
        due = metrics.due_date(window)
        if window in metrics.readings:
            parts.append(f"{window} lida {metrics.readings[window].read_at:%Y-%m-%d}")
        elif today >= due:
            parts.append(f"{window} VENCIDA {due:%Y-%m-%d}")
        else:
            parts.append(f"{window} vence {due:%Y-%m-%d}")
    return "; ".join(parts)


CSV_COLUMNS = [
    "id", "platform", "channel", "format", "series", "published_at", "duration_s", "hypothesis",
    "window", "due", "read_at", *READING_NUMBERS, "traffic_sources", "requests", "notes", "url", "post_id",
]


def table_rows(items: list[PublicationMetrics]) -> list[dict[str, Any]]:
    """Uma linha por janela (lida ou não), para comparar iguais com iguais (AP-10). Ausência fica vazia."""
    rows: list[dict[str, Any]] = []
    for metrics in items:
        base = {
            "id": metrics.id, "platform": metrics.platform, "channel": metrics.channel,
            "format": metrics.format, "series": metrics.series or "",
            "published_at": metrics.published_at.isoformat(), "duration_s": metrics.duration_s,
            "hypothesis": metrics.hypothesis or "", "url": metrics.url or "",
            "post_id": metrics.post_id or "",
            "requests": "; ".join(f"{r.kind}: {r.summary}" for r in metrics.requests),
        }
        for window in WINDOW_DAYS:
            row = {**base, "window": window, "due": metrics.due_date(window).isoformat()}
            reading = metrics.readings.get(window)
            if reading is not None:
                row["read_at"] = reading.read_at.isoformat()
                row.update({name: getattr(reading, name) for name in READING_NUMBERS})
                sources = reading.traffic_sources
                row["traffic_sources"] = "; ".join(f"{s.name} {s.percent:g}%" for s in sources)
                row["notes"] = reading.notes
            rows.append(row)
    return rows


def write_table(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: ("" if row.get(key) is None else row.get(key, "")) for key in CSV_COLUMNS})
