import argparse
from pathlib import Path

import pytest

from app.cli import COMMANDS, EXIT_NOT_IMPLEMENTED, HANDLERS, main
from app.pipeline.ports import Context
from tests.fakes import make_root

# Comandos do CLAUDE.md §10; um comando não pode sumir sem atualizar a spec.
SPEC_COMMANDS = {
    "bench", "new", "sources", "script", "scenes", "assets", "gallery",
    "voice", "subs", "render", "export", "approve", "status",
}


def test_commands_match_spec() -> None:
    assert {c.name for c in COMMANDS} == SPEC_COMMANDS


def test_help_lists_every_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for name in SPEC_COMMANDS:
        assert name in out


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("vp ")


@pytest.mark.parametrize(
    ("argv", "step"),
    [
        (["bench"], 5),
        (["new", "pilot-001", "--topic", "Greely expedition"], 12),
        (["script", "pilot-001"], 27),
        (["render", "pilot-001", "--preview"], 13),
        (["approve", "pilot-001", "--step", "script"], 12),
    ],
)
def test_stub_points_to_roadmap_step(argv: list[str], step: int, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(argv) == EXIT_NOT_IMPLEMENTED
    assert f"etapa #{step}" in capsys.readouterr().err


@pytest.mark.parametrize(
    "argv",
    [
        [],                        # sem comando
        ["script"],                # sem id
        ["new", "pilot-001"],      # sem --topic
        ["approve", "pilot-001"],  # sem --step
    ],
)
def test_invalid_usage_exits_2(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(argv)
    assert exc.value.code == 2


def test_handler_receives_context_built_from_project_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    received: list[Context] = []

    def handler(args: argparse.Namespace, context: Context) -> int:
        received.append(context)
        return 0

    monkeypatch.setitem(HANDLERS, "status", handler)
    root = make_root(tmp_path)
    (root / "data" / "episodes").mkdir(parents=True)
    monkeypatch.chdir(root / "data" / "episodes")  # sobe até achar config/providers.toml
    assert main(["status", "pilot-001"]) == 0
    assert received[0].settings.data_dir == root / "data"


def test_missing_config_is_a_clear_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(HANDLERS, "status", lambda args, context: 0)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match="config/providers.toml não encontrado"):
        main(["status", "pilot-001"])
