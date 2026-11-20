"""Testes de `mais_vistos.py` (skill `vp-validacao-de-tema`): os mais vistos de um canal e a mediana dele."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "vp-validacao-de-tema"


def _load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, SKILL / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


mv = _load("mais_vistos")


def _entry(video_id: str, views: int | None, duration: float | None, title: str = "") -> dict[str, Any]:
    return {"id": video_id, "view_count": views, "duration": duration, "title": title or f"title {video_id}"}


# Forma da saída de `yt-dlp -J --flat-playlist <canal>/videos`, reduzida aos campos lidos.
LISTING: dict[str, Any] = {
    "channel": "Canal de Exemplo",
    "channel_follower_count": 481000,
    "entries": [
        _entry("novo", 1000, 1190.0),
        _entry("hit", 1500000, 5018.0, "The Most Important Ideas"),
        _entry("medio", 107000, 1285.0),
        _entry("alto", 600000, 1001.0),
        _entry("curto", 9000000, 58.0),
        _entry("estreia", None, 900.0),
        None,
    ],
}


def test_rank_orders_by_views_and_drops_short_videos() -> None:
    result = mv.rank(LISTING, {})

    assert [row["id"] for row in result["linhas"]] == ["hit", "alto", "medio", "novo"]
    assert result["canal"] == "Canal de Exemplo"
    assert result["inscritos"] == 481000


def test_rank_leaves_videos_without_view_count_out_of_the_median() -> None:
    result = mv.rank(LISTING, {})

    assert result["videos"] == 4
    assert result["sem_views"] == 1
    # Quatro contados (1000, 107000, 600000, 1500000): o maior dos dois valores centrais.
    assert result["mediana"] == 600000


def test_rank_reports_times_the_channel_median() -> None:
    rows = {row["id"]: row for row in mv.rank(LISTING, {})["linhas"]}

    assert rows["hit"]["vezes"] == 2.5
    assert rows["alto"]["vezes"] == 1.0
    assert rows["medio"]["vezes"] == 0.2


def test_rank_prefers_the_title_from_the_portuguese_reading() -> None:
    rows = {row["id"]: row for row in mv.rank(LISTING, {"hit": "As Ideias Mais Importantes"})["linhas"]}

    assert rows["hit"]["titulo"] == "As Ideias Mais Importantes"
    assert rows["alto"]["titulo"] == "title alto"


def test_rank_respects_n_and_minimum_duration() -> None:
    result = mv.rank(LISTING, {}, n=2, min_s=0)

    assert [row["id"] for row in result["linhas"]] == ["curto", "hit"]
    assert result["videos"] == 5


def test_rank_of_empty_listing_has_no_median() -> None:
    result = mv.rank({"entries": []}, {})

    assert result["videos"] == 0
    assert result["mediana"] == 0
    assert result["linhas"] == []


def test_titles_ignores_empty_entries() -> None:
    listing = {"entries": [_entry("a", 312, 600.0, "Título A"), None, {"id": "b"}]}

    assert mv.titles(listing) == {"a": "Título A"}


def test_render_prints_header_and_one_line_per_video() -> None:
    lines = mv.render(mv.rank(LISTING, {}, n=1))

    assert lines == [
        "# Canal de Exemplo | inscritos=481000 | videos=4 | sem_views=1 | mediana_views=600000 | min_s=300",
        "   1500000 |    2.5x |  83:38 | hit | The Most Important Ideas",
    ]


def test_main_reads_the_portuguese_titles_beside_the_listing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    listing = tmp_path / "canal.json"
    listing.write_text(json.dumps(LISTING), encoding="utf-8")
    # Na leitura com lang=pt as views vêm erradas ("1,5 mi" lido como 1): só o título é aproveitado.
    wrong_views = {"entries": [_entry("hit", 1, 5018.0, "As Ideias Mais Importantes")]}
    (tmp_path / "canal.pt.json").write_text(json.dumps(wrong_views), encoding="utf-8")

    assert mv.main([str(listing), "--n", "1"]) == 0

    out = capsys.readouterr().out.splitlines()
    assert out[1] == "   1500000 |    2.5x |  83:38 | hit | As Ideias Mais Importantes"


def test_main_fails_when_the_listing_has_no_counted_video(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    listing = tmp_path / "canal.json"
    listing.write_text(json.dumps({"entries": [_entry("estreia", None, 900.0)]}), encoding="utf-8")

    assert mv.main([str(listing)]) == 2

    assert "aba /videos" in capsys.readouterr().err
