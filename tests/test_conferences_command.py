"""RF7: `vp medicao` e `vp traducao` dizem cada problema, o resultado e saem com 1 só se há problema."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from tests.test_medicao import EPISODE, MEDICAO, make_store
from tests.test_translation import TARGET, pair


def run(command: str, episode: str, store: object) -> int:
    args = build_parser().parse_args([command, episode])
    context = SimpleNamespace(store=store)
    return handled(f"vp {command}", lambda: HANDLERS[command](args, context))  # type: ignore[arg-type]


def test_traducao_clean_says_so_and_exits_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    store, _ = pair(tmp_path)
    assert run("traducao", TARGET, store) == 0
    assert capsys.readouterr().out == "resultado: sem problemas\n"


def test_traducao_lists_each_problem_and_exits_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store, _ = pair(tmp_path, en_text="One million nodes.")
    assert run("traducao", TARGET, store) == 1
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("- ") and lines[-1] == "resultado: 1 problema(s)"


def test_medicao_clean_says_so_and_exits_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run("medicao", EPISODE, make_store(tmp_path)) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "resultado: sem problemas"


def test_medicao_reports_problems_and_exits_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run("medicao", EPISODE, make_store(tmp_path, medicao=None)) == 1
    out = capsys.readouterr().out.splitlines()
    assert "falta arquivo" in out[0] and out[-1] == "resultado: 1 problema(s)"


def test_medicao_prints_warnings_without_failing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    extra = {**MEDICAO, "numeros": [*MEDICAO["numeros"], {"valor": 7, "nota": "sobra"}]}
    assert run("medicao", EPISODE, make_store(tmp_path, medicao=extra)) == 0
    assert capsys.readouterr().out.splitlines() == [
        "- aviso: medicao.json, número 11 (7): declarado e não usado na fala nem na tela",
        "resultado: sem problemas",
    ]
