import pytest

from app.pipeline.cli import COMMANDS, EXIT_NOT_IMPLEMENTED, main

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
