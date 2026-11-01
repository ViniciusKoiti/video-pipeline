"""RF7: `vp export livros` põe o bloco de livros na descrição e falha com mensagem, sem escrever nada."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.pipeline.constants.affiliate_constants import AffiliateConstants
from app.storage.json_files import JsonFileStore

EP = "ep-livros"
BOOKS = {"livros": [{"titulo": "A República", "autor": "Platão"}]}


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "canal.toml").write_text('[amazon]\ntag = "canal-20"\n', encoding="utf-8")
    folder = tmp_path / "data" / "episodes" / EP
    folder.mkdir(parents=True)
    (folder / "livros.json").write_text(json.dumps(BOOKS), encoding="utf-8")
    return tmp_path


def run(root: Path) -> int:
    args = build_parser().parse_args(["export", "livros", EP])
    store = JsonFileStore(root / "data" / "episodes")
    context = SimpleNamespace(store=store, settings=SimpleNamespace(data_dir=root / "data"))
    return handled("vp export", lambda: HANDLERS["export"](args, context))  # type: ignore[arg-type]


def description(root: Path) -> Path:
    return root / "data" / "episodes" / EP / "description.txt"


def test_the_block_goes_after_the_existing_text_and_a_repeat_changes_nothing(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    description(root).write_text("Resumo do vídeo.\n", encoding="utf-8")
    assert run(root) == 0
    out = capsys.readouterr().out
    assert "tag=canal-20" in out and out.rstrip().endswith("gravado")
    text = description(root).read_text(encoding="utf-8")
    assert text.startswith("Resumo do vídeo.\n\n" + AffiliateConstants.BLOCK_START)
    assert text.rstrip().endswith(AffiliateConstants.DISCLOSURE)
    assert run(root) == 0
    assert "já estava em dia" in capsys.readouterr().out
    assert description(root).read_text(encoding="utf-8") == text


def test_a_description_that_does_not_exist_yet_is_created_with_the_block(root: Path) -> None:
    assert run(root) == 0
    assert description(root).read_text(encoding="utf-8").startswith(AffiliateConstants.BLOCK_START)


def test_a_missing_list_is_an_error_and_writes_nothing(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (root / "data" / "episodes" / EP / "livros.json").unlink()
    assert run(root) == 1
    assert f"vp export: {EP}/livros.json não existe" in capsys.readouterr().err
    assert not description(root).exists()


def test_a_link_outside_amazon_stops_before_touching_the_description(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = {"livros": [{"titulo": "A", "autor": "B", "link": "https://exemplo.com/livro"}]}
    (root / "data" / "episodes" / EP / "livros.json").write_text(json.dumps(bad), encoding="utf-8")
    description(root).write_text("Antes.\n", encoding="utf-8")
    assert run(root) == 1
    assert "link fora da Amazon (exemplo.com)" in capsys.readouterr().err
    assert description(root).read_text(encoding="utf-8") == "Antes.\n"


def test_a_list_outside_the_format_is_an_error(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (root / "data" / "episodes" / EP / "livros.json").write_text('{"livros": [{"titulo": "A"}]}')
    assert run(root) == 1
    assert "livros.json: fora do formato" in capsys.readouterr().err


def test_a_missing_tag_or_config_is_an_error(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (root / "config" / "canal.toml").write_text("[amazon]\n", encoding="utf-8")
    assert run(root) == 1
    assert "falta [amazon] tag" in capsys.readouterr().err
    (root / "config" / "canal.toml").unlink()
    assert run(root) == 1
    assert "config/canal.toml: não foi possível ler" in capsys.readouterr().err
    assert not description(root).exists()


def test_an_up_to_date_description_is_not_written_again(root: Path) -> None:
    assert run(root) == 0
    os.utime(description(root), ns=(1_000_000_000, 1_000_000_000))
    assert run(root) == 0
    assert description(root).stat().st_mtime_ns == 1_000_000_000  # nem o arquivo foi tocado


def test_a_busy_episode_stops_the_command_without_writing(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = JsonFileStore(root / "data" / "episodes")
    with store.lock(EP):
        assert run(root) == 1
    assert "vp export:" in capsys.readouterr().err
    assert not description(root).exists()
