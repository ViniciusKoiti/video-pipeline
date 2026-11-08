"""ADR 045: um handler só na borda para os erros esperados; bug continua com traceback."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from app import cli
from app.cli import main
from app.commands.errors import run
from app.errors import PipelineError
from app.pipeline.check_report import load_check_report
from app.pipeline.gates import GateError
from app.pipeline.ports import EpisodeLocked, ImmutableManifest
from app.pipeline.schemas import CheckVerdict
from tests.fakes import make_root

# Cada classe de erro do projeto e a base que ela já tinha: `except ValueError` e afins seguem pegando-as.
COMPATIBLE = [
    ("app.pipeline.gates", "GateError", ValueError),
    ("app.pipeline.state", "InvalidTransition", ValueError),
    ("app.pipeline.state", "StaleApproval", RuntimeError),
    ("app.pipeline.state", "OutputMissing", RuntimeError),
    ("app.pipeline.state", "InputChanged", RuntimeError),
    ("app.pipeline.ports", "ManifestNotFound", LookupError),
    ("app.pipeline.ports", "ImmutableManifest", PermissionError),
    ("app.pipeline.ports", "EpisodeLocked", RuntimeError),
    ("app.pipeline.sources", "SourceError", ValueError),
    ("app.pipeline.assets", "AssetError", ValueError),
    ("app.pipeline.assets", "NoArchiveAvailable", RuntimeError),
    ("app.pipeline.usage", "UsageError", ValueError),
    ("app.pipeline.format_decision", "FormatNotConfirmed", LookupError),
    ("app.bootstrap.registry", "ConfigurationError", ValueError),
    ("app.commands.postiz_cadeia", "ChainError", ValueError),
    ("app.media.earshot", "EarshotError", RuntimeError),
    ("app.media.evolution", "EvolutionError", RuntimeError),
    ("app.media.host", "SpriteCheckError", RuntimeError),
    ("app.media.loudness", "LoudnessError", RuntimeError),
    ("app.media.pauses", "SplitError", RuntimeError),
    ("app.media.probe", "ProbeError", RuntimeError),
    ("app.render.ffmpeg", "RenderError", RuntimeError),
    ("app.render.remotion", "RemotionError", RuntimeError),
    ("app.providers.errors", "ProviderError", Exception),
    ("app.providers.errors", "QuotaExhausted", Exception),
    ("app.providers.http", "TransportError", Exception),
]


@pytest.mark.parametrize(("module", "name", "old_base"), COMPATIBLE)
def test_every_project_error_is_a_pipeline_error_and_keeps_its_old_base(
    module: str, name: str, old_base: type[BaseException]
) -> None:
    error = getattr(importlib.import_module(module), name)
    assert issubclass(error, PipelineError) and issubclass(error, old_base)


# --- O handler ----------------------------------------------------------------------------------


def test_a_handled_error_prints_the_label_and_the_message_and_exits_with_one(
    capsys: pytest.CaptureFixture[str],
) -> None:
    def action() -> int:
        raise GateError("falta scenes.json")

    assert run("vp approve", action) == 1
    captured = capsys.readouterr()
    assert captured.err == "vp approve: falta scenes.json\n" and captured.out == ""


@pytest.mark.parametrize(("returned", "expected"), [(None, 0), (0, 0), (3, 3), (1, 1)])
def test_the_return_value_of_a_successful_action_is_kept(returned: int | None, expected: int) -> None:
    assert run("vp x", lambda: returned) == expected


def test_a_bug_is_not_swallowed_and_keeps_its_traceback() -> None:
    def action() -> int:
        raise KeyError("bug")

    with pytest.raises(KeyError):
        run("vp x", action)


def test_vp_debug_lets_the_handled_error_rise_with_its_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    def action() -> int:
        raise EpisodeLocked("ep já está em uso")

    monkeypatch.setenv("VP_DEBUG", "1")
    with pytest.raises(EpisodeLocked):
        run("vp x", action)
    monkeypatch.delenv("VP_DEBUG")
    assert run("vp x", action) == 1


def test_the_cli_handles_an_error_that_no_command_listed_before(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`ImmutableManifest` não estava na lista de `approve`/`reopen` e escaparia como traceback."""

    def writes_an_approved_file(args: object, context: object) -> int:
        raise ImmutableManifest("ep/sources.json está carimbado pelo gate de sources")

    monkeypatch.chdir(make_root(tmp_path))
    monkeypatch.setitem(cli.HANDLERS, "status", writes_an_approved_file)
    assert main(["status", "ep"]) == 1
    assert capsys.readouterr().err == "vp status: ep/sources.json está carimbado pelo gate de sources\n"


# --- O parecer do verificador é lido uma vez, na entrada ----------------------------------------


def test_the_check_report_loader_turns_every_bad_file_into_a_gate_error(tmp_path: Path) -> None:
    good = tmp_path / "parecer.json"
    good.write_text('{"verdict": "rejected", "problems": ["DIVERGE S03", 7]}')
    assert load_check_report(good) == (CheckVerdict.REJECTED, ["DIVERGE S03", "7"])
    cases = {
        "ausente.json": None,
        "vazio.json": "",
        "talvez.json": '{"verdict": "talvez"}',
        "sem-veredito.json": '{"problems": []}',
        "lista.json": "[1, 2]",
        "problemas.json": '{"verdict": "approved", "problems": 3}',
    }
    for name, content in cases.items():
        path = tmp_path / name
        if content is not None:
            path.write_text(content)
        with pytest.raises(GateError, match=f"{name}: parecer inválido"):
            load_check_report(path)


def test_vp_checagem_reports_an_invalid_report_through_the_handler(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    report = tmp_path / "parecer.json"
    report.write_text('{"verdict": "talvez"}')
    monkeypatch.chdir(make_root(tmp_path))
    assert main(["checagem", "ep", str(report)]) == 1
    assert capsys.readouterr().err.startswith("vp checagem: parecer.json: parecer inválido")
