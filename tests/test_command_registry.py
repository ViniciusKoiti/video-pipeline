"""RF4: o registro de comandos preserva argumentos e códigos de saída, sem descoberta dinâmica de módulos."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app.cli import HANDLERS, build_parser, main
from app.commands.constants.cli_constants import CliConstants

APP = Path(__file__).resolve().parents[1] / "app"
# Registrados à parte, com subcomandos próprios (módulos de app/commands).
OWN_PARSERS = {
    "postiz", "usage", "sources", "assets", "briefs", "music", "export", "metricas", "short", "audio",
}
COMMAND_NAMES = [c.name for c in CliConstants.COMMANDS]


def test_command_names_are_unique_and_every_handler_has_a_command() -> None:
    assert len(COMMAND_NAMES) == len(set(COMMAND_NAMES))
    assert set(HANDLERS) - OWN_PARSERS <= set(COMMAND_NAMES)
    assert set(HANDLERS) >= OWN_PARSERS


@pytest.mark.parametrize("name", sorted(set(HANDLERS) - OWN_PARSERS))
def test_each_handler_command_keeps_its_declared_arguments(name: str) -> None:
    command = next(c for c in CliConstants.COMMANDS if c.name == name)
    parser = build_parser()
    needs = {
        "approve": ["--step", "sources"],
        "reject": ["--step", "script", "--reason", "x"],
        "reopen": ["--step", "sources", "--reason", "x"],
        "checagem": ["parecer.json"],
    }
    argv = [name, *(["ep"] if command.takes_episode else []), *needs.get(name, [])]
    if name == "bench":
        argv = ["bench"]
    args = parser.parse_args(argv)
    assert args.command == name
    assert getattr(args, "episode_id", None) == ("ep" if command.takes_episode else None)
    if command.takes_episode:
        with pytest.raises(SystemExit) as missing:  # sem o id, o argparse recusa com 2
            parser.parse_args([name])
        assert missing.value.code == 2


def test_commands_without_a_handler_exit_with_the_not_implemented_code(
    capsys: pytest.CaptureFixture[str],
) -> None:
    stubs = [c.name for c in CliConstants.COMMANDS if c.name not in HANDLERS]
    assert {
        "new",
        "script",
        "scenes",
        "gallery",
        "subs",
    } <= set(stubs)
    assert main(["script", "ep"]) == CliConstants.EXIT_NOT_IMPLEMENTED == 3
    assert "ainda não implementado" in capsys.readouterr().err


LOADERS = {"pkgutil", "importlib", "importlib.util", "importlib.machinery", "importlib.resources"}


def test_there_is_no_dynamic_module_discovery() -> None:
    """Todo comando entra em `HANDLERS` por import explícito. `importlib.metadata` (a versão do pacote) pode;
    `import_module`, `pkgutil` e `__import__` não."""
    problems = []
    for path in [APP / "cli.py", *(APP / "commands").glob("*.py")]:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                problems += [f"{path.name}: import {a.name}" for a in node.names if a.name in LOADERS]
            elif isinstance(node, ast.ImportFrom):
                loaded = node.module in LOADERS or any(a.name == "import_module" for a in node.names)
                problems += [f"{path.name}: from {node.module} import ..."] if loaded else []
            elif isinstance(node, ast.Name) and node.id == "__import__":
                problems.append(f"{path.name}: usa __import__")
    assert problems == []
