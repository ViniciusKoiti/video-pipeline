from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import cli
from tests.fakes import make_root


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(make_root(tmp_path))
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    return tmp_path


def test_help_does_not_create_database(root: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["usage", "--help"])
    assert exc.value.code == 0
    assert not (root / "data/telemetry").exists()


def test_cli_can_initialize_reserve_import_and_report(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["usage", "init"]) == 0
    assert Path(json.loads(capsys.readouterr().out)["database"]).is_file()
    assert (
        cli.main(
            [
                "usage",
                "budget",
                "pilot",
                "--id",
                "tokens",
                "--metric",
                "tokens_total",
                "--limit",
                "100",
            ]
        )
        == 0
    )
    assert (
        cli.main(
            [
                "usage",
                "start",
                "pilot",
                "--id",
                "r1",
                "--stage",
                "roteiro",
                "--agent",
                "roteirista",
            ]
        )
        == 0
    )
    allocations = root / "allocations.json"
    allocations.write_text('{"tokens":70}')
    assert cli.main(["usage", "reserve", "r1", str(allocations)]) == 0
    events = root / "events.jsonl"
    events.write_text(
        json.dumps(
            {
                "request_id": "req-1",
                "model": "test",
                "event.timestamp": "2026-10-24T12:00:00Z",
                "input_tokens": 10,
                "output_tokens": 5,
                "cache_read_tokens": 20,
                "cache_creation_tokens": 5,
                "cost_usd_micros": 7,
            }
        )
        + "\n"
    )
    assert cli.main(["usage", "import", "r1", str(events)]) == 0
    assert cli.main(["usage", "import", "r1", str(events)]) == 0
    capsys.readouterr()
    assert cli.main(["usage", "report", "pilot"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["models"][0]["requests"] == 1
    assert report["budgets"][0]["available_value"] == 30
    assert cli.main(["usage", "finish", "r1", "--reconciled"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "closed"


def test_invalid_batch_is_not_partially_imported_or_echoed(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cli.main(["usage", "start", "pilot", "--id", "r1", "--stage", "roteiro", "--agent", "roteirista"])
    events = root / "events.jsonl"
    events.write_text(
        '{"event_key":"ok","model":"test","occurred_at":"2026-10-24T12:00:00Z"}\n'
        '{"event_key":"bad","model":"test","input_tokens":"private-sentinel"}\n'
    )
    capsys.readouterr()
    assert cli.main(["usage", "import", "r1", str(events)]) == 1
    output = capsys.readouterr()
    assert json.loads(output.err)["error"]
    assert "private-sentinel" not in output.err
    assert "Traceback" not in output.err
    assert output.out == ""
    cli.main(["usage", "report", "pilot"])
    assert json.loads(capsys.readouterr().out)["models"] == []


@pytest.mark.parametrize("payload", ['{"tokens":true}', "[]", "not-json"])
def test_invalid_allocations_are_safe_json_errors(
    root: Path, capsys: pytest.CaptureFixture[str], payload: str
) -> None:
    path = root / "allocations.json"
    path.write_text(payload)
    assert cli.main(["usage", "reserve", "missing", str(path)]) == 1
    assert json.loads(capsys.readouterr().err)["error"]


def test_missing_subcommand_is_an_argument_error(root: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["usage"])
    assert exc.value.code == 2


def test_missing_project_configuration_is_safe_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    assert cli.main(["usage", "init"]) == 1
    assert json.loads(capsys.readouterr().err)["error"]


def test_invalid_settings_do_not_echo_secret(
    root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("ALLOW_PAID_API", "private-invalid-sentinel")
    assert cli.main(["usage", "init"]) == 1
    output = capsys.readouterr()
    assert json.loads(output.err)["error"]
    assert "private-invalid-sentinel" not in output.err
    assert "Traceback" not in output.err
