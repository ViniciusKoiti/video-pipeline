"""RF7: `vp sources` (add e declared) registra pelo `SourceRegistry`, com os argumentos dos scripts."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.pipeline.gates import record_decision
from app.pipeline.schemas import Decision, SourcesManifest, Step
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.test_sources import EP, HTML, NOW


@pytest.fixture
def data(tmp_path: Path) -> JsonFileStore:
    store = JsonFileStore(tmp_path / "episodes")
    store.write(EP, "sources.json", SourcesManifest(episode_id=EP, sources=[]))
    store.path(EP, "facts.json").write_text("{}")
    return store


def run(data: JsonFileStore, tmp_path: Path, *argv: str) -> int:
    """O caminho real do comando: parser do `vp`, `HANDLERS` e o handler central de erros (ADR 045)."""
    args = build_parser().parse_args(["sources", *argv])
    context = SimpleNamespace(
        store=data, review=JsonReviewGate(data), settings=SimpleNamespace(data_dir=tmp_path)
    )
    return handled("vp sources", lambda: HANDLERS["sources"](args, context))  # type: ignore[arg-type]


def ids(store: JsonFileStore) -> list[str]:
    return [s.id for s in store.read(EP, "sources.json", SourcesManifest).sources]


def test_add_with_a_saved_file_registers_and_a_repeat_is_idempotent(
    data: JsonFileStore, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    page = tmp_path / "pagina.html"
    page.write_bytes(HTML)
    args = (
        EP,
        "https://exemplo.org/a",
        "--title",
        "Fonte A",
        "--kind",
        "secondary",
        "--file",
        str(page),
        "--authors",
        "Silva, Ana; Souza, Bia",
        "--interested",
    )
    assert run(data, tmp_path, "add", *args) == 0
    assert "source-01: html, 2 trechos" in capsys.readouterr().out
    [source] = data.read(EP, "sources.json", SourcesManifest).sources
    assert (source.authors, source.interested, source.url) == (
        ["Silva, Ana", "Souza, Bia"],
        True,
        "https://exemplo.org/a",
    )
    assert run(data, tmp_path, "add", *args) == 0  # repetir não é erro nem duplica
    assert "já registrada" in capsys.readouterr().out and ids(data) == ["source-01"]


def test_declared_registers_lines_as_excerpts(
    data: JsonFileStore, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    note = tmp_path / "nota.md"
    note.write_text("2 ovos\n1 xícara de farinha\n")
    assert run(data, tmp_path, "declared", EP, str(note), "--title", "Receita") == 0
    assert "source-01: fonte declarada, 2 trechos" in capsys.readouterr().out
    assert "[source-01#E2] 1 xícara de farinha" in data.path(EP, "excerpts/source-01.md").read_text()


def test_an_approved_gate_one_stops_the_command_with_a_message(
    data: JsonFileStore, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    review = JsonReviewGate(data)
    record_decision(data, review, EP, Step.SOURCES, Decision.APPROVED, reviewer="Dono", now=lambda: NOW)
    note = tmp_path / "nota.md"
    note.write_text("um\n")
    assert run(data, tmp_path, "declared", EP, str(note), "--title", "Nota") == 1
    assert "vp sources: ep-fontes/sources.json está carimbado pelo gate de sources" in capsys.readouterr().err
    assert run(data, tmp_path, "declared", EP, str(tmp_path / "nada.md"), "--title", "Nota") == 1
    assert "não existe" in capsys.readouterr().err
    assert ids(data) == []


def test_the_command_needs_a_subcommand_and_a_valid_kind(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as no_subcommand:
        build_parser().parse_args(["sources"])
    with pytest.raises(SystemExit) as bad_kind:
        build_parser().parse_args(["sources", "add", EP, "https://x.org", "--title", "T", "--kind", "blog"])
    assert (no_subcommand.value.code, bad_kind.value.code) == (2, 2)
    assert "invalid choice" in capsys.readouterr().err
