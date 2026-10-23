"""Métricas de publicação (§12, contrato D6): schema, registro do Postiz, leituras, pendências e tabela."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from datetime import UTC, date, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from pydantic import ValidationError

from app.cli import main
from app.pipeline.check import check_episode
from app.pipeline.metrics import (
    all_metrics,
    load_metrics,
    metrics_path,
    pending_lines,
    record_reading,
    registry_path,
    save_metrics,
    scheduled_posts,
    summary_line,
    table_rows,
    write_table,
)
from app.pipeline.schemas import MetricsReading, PublicationMetrics
from app.storage.json_files import JsonFileStore
from tests.fakes import REPO_ROOT, make_root

EPISODE = "ensaio-teste"
PUBLISHED = datetime(2026, 10, 20, 22, 0, tzinfo=UTC)
MEDIA = f"data/episodes/{EPISODE}/renders/final.mp4"


def metrics(**changes: Any) -> PublicationMetrics:
    data = {"id": EPISODE, "platform": "youtube", "channel": "Cena e Conceito", "format": "longo",
            "published_at": PUBLISHED.isoformat(), **changes}
    return PublicationMetrics.model_validate(data)


def reading(**changes: Any) -> MetricsReading:
    return MetricsReading.model_validate({"read_at": "2026-10-27", "views": 1200, **changes})


# --- contrato ---------------------------------------------------------------------------------------


def test_due_dates_follow_the_published_timezone() -> None:
    m = metrics()
    assert m.due_date("d7") == date(2026, 10, 27) and m.due_date("d28") == date(2026, 11, 17)
    assert m.pending(date(2026, 10, 26)) == [] and m.upcoming(date(2026, 10, 26)) == ["d7", "d28"]
    assert m.pending(date(2026, 10, 27)) == ["d7"]
    assert m.pending(date(2026, 12, 1)) == ["d7", "d28"] and m.upcoming(date(2026, 12, 1)) == []


def test_reading_needs_a_number_and_keeps_what_was_not_read_as_null() -> None:
    with pytest.raises(ValidationError, match="sem nenhum número"):
        MetricsReading.model_validate({"read_at": "2026-10-27"})
    r = reading()
    assert r.likes is None and json.loads(r.model_dump_json())["likes"] is None


def test_reading_rejects_percentages_out_of_range_and_duplicate_sources() -> None:
    with pytest.raises(ValidationError):
        reading(ctr_percent=120)
    with pytest.raises(ValidationError, match="acima de 100"):
        reading(traffic_sources=[{"name": "Navegação", "percent": 70}, {"name": "Sugeridos", "percent": 40}])
    with pytest.raises(ValidationError, match="duplicad"):
        reading(traffic_sources=[{"name": "Navegação", "percent": 10}, {"name": "Navegação", "percent": 5}])


def test_reading_before_the_window_closes_is_refused() -> None:
    with pytest.raises(ValidationError, match="só fecha em 2026-10-27"):
        metrics(readings={"d7": {"read_at": "2026-10-26", "views": 10}})
    assert metrics(readings={"d7": {"read_at": "2026-10-27", "views": 10}}).readings["d7"].views == 10
    with pytest.raises(ValidationError):
        metrics(readings={"d9": {"read_at": "2026-10-29", "views": 10}})


def test_record_reading_is_once_per_window_unless_replaced() -> None:
    m = record_reading(metrics(), "d7", reading())
    with pytest.raises(ValueError, match="já lida em 2026-10-27"):
        record_reading(m, "d7", reading(views=1))
    again = record_reading(m, "d7", reading(views=1, read_at=date(2026, 10, 28)), replace=True)
    assert again.readings["d7"].views == 1 and m.readings["d7"].views == 1200
    with pytest.raises(ValidationError, match="só fecha"):
        record_reading(m, "d28", reading(read_at=date(2026, 11, 1)))


# --- registro do Postiz -----------------------------------------------------------------------------


def package(payload: str, when: str, channel: str, channel_id: str, media: str, episode: str | None) -> dict:
    return {
        "at": "2026-10-19T20:56:00+00:00", "event": "pacote", "payload": payload,
        "o_que": {"data": when, "posts": [{"canal": channel, "canal_id": channel_id, "legenda": "…",
                                            "midia": [{"id": "m", "arquivo": media, "sha256": "sha256:0"}]}]},
        "evidencia": {"episodio": episode, "gate_4": "aprovado" if episode else "sem episódio"},
    }


def registry(tmp_path: Path) -> Path:
    when = PUBLISHED.isoformat()
    rows = [
        {"at": "2026-10-19T20:00:00+00:00", "event": "upload", "payload": "sha256:aaa"},
        package("sha256:aaa", when, "Cena e Conceito", "int-yt", MEDIA, EPISODE),
        package("sha256:aaa", when, "Cena e Conceito", "int-yt", MEDIA, EPISODE),  # pacote refeito
        {"at": "2026-10-19T21:00:00+00:00", "event": "duvida", "payload": "sha256:aaa", "veredito": "segue"},
        {"at": "2026-10-20T01:10:00+00:00", "event": "agendado", "payload": "sha256:aaa", "data": when,
         "posts": [{"postId": "post-1", "integration": "int-yt"}]},
        package("sha256:bbb", "2026-10-17T00:00:00+00:00", "Nabote Songs", "int-nb", "renders/clipe/x.mp4",
                None),
        {"at": "2026-10-16T23:34:00+00:00", "event": "agendado", "payload": "sha256:bbb",
         "data": "2026-10-17T00:00:00+00:00", "posts": [{"postId": "post-2", "integration": "int-nb"}]},
        package("sha256:ccc", when, "Cena e Conceito", "int-yt", MEDIA, "nunca-agendado"),
    ]
    path = registry_path(tmp_path / "data")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    return path


def test_scheduled_posts_pair_package_and_schedule_by_payload(tmp_path: Path) -> None:
    posts = scheduled_posts(registry(tmp_path))
    assert [(p.episode_id, p.channel, p.integration_id, p.post_id, p.media) for p in posts] == [
        (EPISODE, "Cena e Conceito", "int-yt", "post-1", MEDIA),
        (None, "Nabote Songs", "int-nb", "post-2", "renders/clipe/x.mp4"),
    ]
    assert posts[0].scheduled_at == PUBLISHED
    assert scheduled_posts(tmp_path / "nada.jsonl") == []


# --- arquivos ---------------------------------------------------------------------------------------


def test_metrics_path_prefers_the_episode_folder(tmp_path: Path) -> None:
    data = tmp_path / "data"
    (data / "episodes" / EPISODE).mkdir(parents=True)
    assert metrics_path(data, EPISODE) == data / "episodes" / EPISODE / "metrics.json"
    assert metrics_path(data, "nabote-clipe") == data / "publicacoes" / "metricas" / "nabote-clipe.json"


def test_save_load_and_list_all(tmp_path: Path) -> None:
    data = tmp_path / "data"
    (data / "episodes" / EPISODE).mkdir(parents=True)
    save_metrics(metrics_path(data, EPISODE), metrics())
    clip = metrics(id="nabote-clipe", channel="Nabote Songs", format="clipe")
    save_metrics(metrics_path(data, "nabote-clipe"), clip)
    items = all_metrics(data)
    assert [m.id for _, m in items] == [EPISODE, "nabote-clipe"]
    assert load_metrics(items[0][0]).published_at == PUBLISHED
    assert not list((data / "episodes" / EPISODE).glob(".*.tmp"))


# --- vp status e vp check ---------------------------------------------------------------------------


def test_status_and_summary_lines() -> None:
    m = metrics()
    assert pending_lines(m, date(2026, 10, 23)) == []
    assert pending_lines(m, date(2026, 10, 30)) == ["métricas d7 (venceu 2026-10-27)"]
    assert summary_line(m, date(2026, 10, 23)) == (
        "publicado 2026-10-20 (youtube, Cena e Conceito); d7 vence 2026-10-27; d28 vence 2026-11-17"
    )
    read = record_reading(m, "d7", reading())
    assert summary_line(read, date(2026, 11, 20)) == (
        "publicado 2026-10-20 (youtube, Cena e Conceito); d7 lida 2026-10-27; d28 VENCIDA 2026-11-17"
    )


def episode_folder(root: Path) -> Path:
    folder = JsonFileStore(root / "data" / "episodes").path(EPISODE, "")
    folder.mkdir(parents=True)
    files = {"sources.json": "{}", "facts.json": "{}", "scenes.json": "{}", "outline.md": "# r\n"}
    for name, text in files.items():
        (folder / name).write_text(text)
    return folder


def test_vp_status_lists_overdue_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = make_root(tmp_path)
    folder = episode_folder(root)
    save_metrics(folder / "metrics.json", metrics(published_at=datetime(2026, 1, 1, 12, tzinfo=UTC)))
    monkeypatch.chdir(root)
    assert main(["status", EPISODE]) == 0
    out = capsys.readouterr().out
    assert "métricas" in out and "d7 VENCIDA 2026-01-08" in out
    assert "métricas d7 (venceu 2026-01-08), métricas d28 (venceu 2026-01-29)" in out
    (folder / "metrics.json").write_text('{"id": "x"}')
    assert main(["status", EPISODE]) == 0
    assert "metrics.json inválido" in capsys.readouterr().out


def test_vp_check_validates_metrics_and_warns_overdue(tmp_path: Path) -> None:
    store = JsonFileStore(tmp_path / "data" / "episodes")
    folder = store.path(EPISODE, "")
    folder.mkdir(parents=True)
    save_metrics(folder / "metrics.json", metrics())
    report = check_episode(store, EPISODE, today=date(2026, 10, 30))
    assert report.ok and any(line.startswith("métricas: publicado 2026-10-20") for line in report.checked)
    assert report.warnings == ["metrics.json: d7 vencida em 2026-10-27 e não lida"]
    (folder / "metrics.json").write_text(json.dumps({"id": EPISODE, "platform": "orkut"}))
    report = check_episode(store, EPISODE, today=date(2026, 10, 30))
    assert not report.ok and report.errors[0].startswith("metrics.json:")


# --- tabela -----------------------------------------------------------------------------------------


def test_table_has_one_row_per_window(tmp_path: Path) -> None:
    m = record_reading(metrics(), "d7", reading(traffic_sources=[{"name": "Navegação", "percent": 42.5}]))
    rows = table_rows([m])
    assert [(r["window"], r["due"], r.get("read_at")) for r in rows] == [
        ("d7", "2026-10-27", "2026-10-27"), ("d28", "2026-11-17", None),
    ]
    assert rows[0]["views"] == 1200 and rows[0]["traffic_sources"] == "Navegação 42.5%"
    out = tmp_path / "metricas.csv"
    write_table(out, rows)
    with out.open(encoding="utf-8", newline="") as handle:
        parsed = list(csv.DictReader(handle))
    assert parsed[0]["views"] == "1200" and parsed[1]["views"] == "" and parsed[1]["likes"] == ""


# --- script provisório ------------------------------------------------------------------------------


def script() -> ModuleType:
    path = REPO_ROOT / "scripts" / "provisorio" / "metricas.py"
    spec = importlib.util.spec_from_file_location("metricas", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def iniciar_args(**changes: Any) -> argparse.Namespace:
    base = {"id": EPISODE, "platform": "youtube", "format": "longo", "channel": None, "published_at": None,
            "post_id": None, "url": None, "series": None, "duration_s": None,
            "hypothesis": "abertura com pergunta"}
    return argparse.Namespace(**{**base, **changes})


def ler_args(**changes: Any) -> argparse.Namespace:
    base = {"id": EPISODE, "janela": "d7", "read_at": date(2026, 10, 27), "views": 1500, "likes": None,
            "shares": None, "comments": 3, "saves": None, "impressions": None, "inscritos": None, "ctr": 4.2,
            "duracao_media": None, "retencao_30s": None, "origem": ["Navegação=42"],
            "pedido": ["duvida: como achar o livro"], "nota": None, "refazer": False}
    return argparse.Namespace(**{**base, **changes})


def test_script_iniciar_ler_pendentes_tabela(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data = tmp_path / "data"
    registry(tmp_path)
    (data / "episodes" / EPISODE).mkdir(parents=True)
    mod = script()
    assert mod.iniciar(iniciar_args(), data) == 0
    path = data / "episodes" / EPISODE / "metrics.json"
    m = load_metrics(path)
    assert m.published_at == PUBLISHED and m.post_id == "post-1" and m.channel == "Cena e Conceito"
    assert m.hypothesis == "abertura com pergunta" and m.readings == {}
    assert mod.iniciar(iniciar_args(), data) == 1  # nunca sobrescreve
    assert mod.iniciar(iniciar_args(id="sem-registro", format="clipe"), data) == 1  # sem data conhecida
    assert mod.iniciar(iniciar_args(id="sem-registro", format="clipe", channel="Nabote Songs",
                                    published_at=PUBLISHED), data) == 0
    assert (data / "publicacoes" / "metricas" / "sem-registro.json").is_file()

    assert mod.ler(ler_args(), data) == 0
    m = load_metrics(path)
    assert m.readings["d7"].views == 1500 and m.readings["d7"].ctr_percent == 4.2
    assert m.readings["d7"].traffic_sources[0].name == "Navegação" and m.requests[0].kind == "duvida"
    assert mod.ler(ler_args(views=1), data) == 1  # segunda leitura sem --refazer
    assert "já lida" in capsys.readouterr().err
    assert mod.ler(ler_args(views=1, refazer=True, pedido=[]), data) == 0
    assert load_metrics(path).readings["d7"].views == 1 and len(load_metrics(path).requests) == 1
    assert mod.ler(ler_args(janela="d28", read_at=date(2026, 11, 1)), data) == 1  # antes da janela
    assert "só fecha" in capsys.readouterr().err

    assert mod.pendentes(argparse.Namespace(hoje=date(2026, 11, 20)), data) == 0
    assert "vencidas e não lidas: 3" in capsys.readouterr().out  # d28 do episódio + d7 e d28 do clipe
    assert mod.tabela(argparse.Namespace(saida=None), data) == 0
    assert (data / "publicacoes" / "metricas.csv").is_file()
