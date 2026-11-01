"""RF5: os scripts de fonte são chamadores finos do registro; mesmos argumentos, sem rede."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.commands.errors import run as handled
from app.pipeline.gates import record_decision
from app.pipeline.schemas import Decision, SourcesManifest, Step
from app.storage.json_files import JsonFileStore, JsonReviewGate
from scripts.provisorio import baixar_fonte, fonte_declarada
from tests.test_sources import EP, HTML, NOW


@pytest.fixture
def data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> JsonFileStore:
    store = JsonFileStore(tmp_path / "episodes")
    store.write(EP, "sources.json", SourcesManifest(episode_id=EP, sources=[]))
    store.path(EP, "facts.json").write_text("{}")
    for module in (baixar_fonte, fonte_declarada):
        monkeypatch.setattr(module, "load_settings", lambda root: SimpleNamespace(data_dir=tmp_path))
        monkeypatch.setattr(module, "ROOT", tmp_path)  # só para a mensagem com o caminho relativo
    return store


def run(module: object, monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    """O ponto de entrada real do script: `main` dentro do handler central (ADR 045)."""
    monkeypatch.setattr(sys, "argv", ["script", *argv])
    return handled("script", module.main)  # type: ignore[attr-defined]


def ids(store: JsonFileStore) -> list[str]:
    return [s.id for s in store.read(EP, "sources.json", SourcesManifest).sources]


def test_baixar_fonte_with_a_saved_file_registers_and_a_repeat_is_idempotent(
    data: JsonFileStore, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
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
    assert run(baixar_fonte, monkeypatch, *args) == 0
    assert "source-01: html, 2 trechos" in capsys.readouterr().out
    [source] = data.read(EP, "sources.json", SourcesManifest).sources
    assert (source.authors, source.interested, source.url) == (
        ["Silva, Ana", "Souza, Bia"],
        True,
        "https://exemplo.org/a",
    )
    assert run(baixar_fonte, monkeypatch, *args) == 0  # repetir não é erro nem duplica
    assert "já registrada" in capsys.readouterr().out and ids(data) == ["source-01"]


def test_fonte_declarada_registers_lines_as_excerpts(
    data: JsonFileStore, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    note = tmp_path / "nota.md"
    note.write_text("2 ovos\n1 xícara de farinha\n")
    assert run(fonte_declarada, monkeypatch, EP, str(note), "--title", "Receita") == 0
    assert "source-01: fonte declarada, 2 trechos" in capsys.readouterr().out
    assert "[source-01#E2] 1 xícara de farinha" in data.path(EP, "excerpts/source-01.md").read_text()


def test_an_approved_gate_one_stops_the_scripts_with_a_message(
    data: JsonFileStore, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    review = JsonReviewGate(data)
    record_decision(data, review, EP, Step.SOURCES, Decision.APPROVED, reviewer="Dono", now=lambda: NOW)
    note = tmp_path / "nota.md"
    note.write_text("um\n")
    assert run(fonte_declarada, monkeypatch, EP, str(note), "--title", "Nota") == 1
    assert "script: ep-fontes/sources.json está carimbado pelo gate de sources" in capsys.readouterr().err
    assert run(fonte_declarada, monkeypatch, EP, str(tmp_path / "nada.md"), "--title", "Nota") == 1
    assert "não existe" in capsys.readouterr().err
    assert ids(data) == []
