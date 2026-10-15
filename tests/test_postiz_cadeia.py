"""Cadeia do agendamento: pacote de decisão antes, registro depois, nada agendado sem pacote (ADR 025)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from app import cli
from app.commands import postiz as postiz_command
from app.providers.errors import ProviderError
from tests.fakes import make_root

EPISODE = "ep-teste"
REGISTRO = Path("data/publicacoes/registro.jsonl")


def payload(media_id: str = "media-1") -> dict:
    return {
        "type": "schedule",
        "date": "2099-10-15T15:30:00.000Z",
        "posts": [
            {
                "integration": {"id": "instagram-1"},
                "value": [
                    {"content": "<p>Nabote: fé</p>", "image": [{"id": media_id, "path": "https://x/v.mp4"}]}
                ],
            }
        ],
    }


@pytest.fixture
def root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(make_root(tmp_path))
    return tmp_path


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Mock:
    client = Mock()
    client.check_schedule.return_value = {
        "date": "2099-10-15T15:30:00+00:00",
        "integrations": {"instagram-1": "Nabote"},
    }
    client.upload.return_value = {"id": "media-1", "path": "https://x/v.mp4"}
    client.schedule.return_value = [{"postId": "post-1", "integration": "instagram-1"}]
    monkeypatch.setattr(postiz_command, "build_postiz", Mock(return_value=client))
    return client


def write_payload(root: Path, data: dict) -> str:
    path = root / "post.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


def doubt(root: Path, path: str, veredito: str = "segue", riscos: list[str] | None = None) -> int:
    report = root / "parecer.json"
    report.write_text(
        json.dumps({"veredito": veredito, "riscos": riscos or [], "revisor": "duvida-cega"}), encoding="utf-8"
    )
    return cli.main(["postiz", "duvida", path, str(report)])


def events(root: Path) -> list[dict]:
    return [json.loads(line) for line in (root / REGISTRO).read_text(encoding="utf-8").splitlines()]


def test_upload_records_file_hash_and_media(root: Path, client: Mock) -> None:
    (root / "reel.mp4").write_bytes(b"video")
    assert cli.main(["postiz", "upload", "reel.mp4"]) == 0
    [upload] = events(root)
    assert upload["event"] == "upload"
    assert upload["arquivo"] == "reel.mp4"
    assert upload["sha256"].startswith("sha256:")
    assert upload["midia"] == {"id": "media-1", "path": "https://x/v.mp4"}


def test_package_lists_what_risks_undo_and_recommendation_without_scheduling(
    root: Path, client: Mock, capsys: pytest.CaptureFixture[str]
) -> None:
    (root / "reel.mp4").write_bytes(b"video")
    cli.main(["postiz", "upload", "reel.mp4"])
    capsys.readouterr()
    assert cli.main(["postiz", "pacote", write_payload(root, payload())]) == 0
    package = json.loads(capsys.readouterr().out)
    [post] = package["o_que"]["posts"]
    assert post["canal"] == "Nabote"
    assert post["legenda"] == "Nabote: fé"
    assert post["midia"][0]["arquivo"] == "reel.mp4"
    assert package["evidencia"]["gate_4"] == "sem episódio"
    assert any("gate 4 não foi conferido" in r for r in package["riscos"])
    assert package["como_desfazer"]
    assert package["recomendacao"].startswith("agendar")
    client.schedule.assert_not_called()
    assert [e["event"] for e in events(root)] == ["upload", "pacote"]


def test_package_flags_media_without_recorded_upload(
    root: Path, client: Mock, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["postiz", "pacote", write_payload(root, payload("outra"))]) == 0
    package = json.loads(capsys.readouterr().out)
    assert any("outra sem envio no registro" in r for r in package["riscos"])


def test_schedule_without_package_is_refused_and_nothing_is_sent(
    root: Path, client: Mock, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["postiz", "schedule", write_payload(root, payload())]) == 1
    assert "pacote" in json.loads(capsys.readouterr().err)["error"]
    client.schedule.assert_not_called()


def test_package_of_another_payload_does_not_authorize(root: Path, client: Mock) -> None:
    cli.main(["postiz", "pacote", write_payload(root, payload())])
    changed = payload()
    changed["date"] = "2099-10-16T15:30:00.000Z"
    assert cli.main(["postiz", "schedule", write_payload(root, changed)]) == 1
    client.schedule.assert_not_called()


def test_schedule_after_package_sends_once_and_records_ids(
    root: Path, client: Mock, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_payload(root, payload())
    cli.main(["postiz", "pacote", path])
    assert doubt(root, path) == 0
    capsys.readouterr()
    assert cli.main(["postiz", "schedule", path]) == 0
    client.schedule.assert_called_once_with(payload())
    assert json.loads(capsys.readouterr().out) == client.schedule.return_value
    package, parecer, scheduled = events(root)
    assert parecer["event"] == "duvida"
    assert scheduled["event"] == "agendado"
    assert scheduled["payload"] == package["payload"]
    assert scheduled["posts"] == client.schedule.return_value


def test_failed_schedule_is_recorded(root: Path, client: Mock) -> None:
    path = write_payload(root, payload())
    cli.main(["postiz", "pacote", path])
    doubt(root, path)
    client.schedule.side_effect = ProviderError("postiz", "envio falhou; consulte a fila antes de repetir")
    assert cli.main(["postiz", "schedule", path]) == 1
    assert events(root)[-1]["event"] == "falha"
    assert "consulte a fila" in events(root)[-1]["erro"]


def approve_preview(root: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    folder = root / "data" / "episodes" / EPISODE
    (folder / "renders").mkdir(parents=True)
    (folder / "renders" / "preview.mp4").write_bytes(b"previa")
    assert cli.main(["approve", EPISODE, "--step", "preview", "--reviewer", "Dono"]) == 0
    return folder


def test_episode_without_approved_preview_recommends_not_scheduling(
    root: Path, client: Mock, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_payload(root, payload())
    assert cli.main(["postiz", "pacote", path, "--episode", EPISODE]) == 0
    package = json.loads(capsys.readouterr().out)
    assert package["evidencia"]["gate_4"] == "não aprovado"
    assert package["recomendacao"].startswith("não agendar")
    assert cli.main(["postiz", "schedule", path]) == 1
    client.schedule.assert_not_called()


def test_preview_changed_after_package_blocks_schedule(
    root: Path, client: Mock, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    folder = approve_preview(root, monkeypatch)
    capsys.readouterr()
    path = write_payload(root, payload())
    assert cli.main(["postiz", "pacote", path, "--episode", EPISODE]) == 0
    assert json.loads(capsys.readouterr().out)["evidencia"]["gate_4"] == "aprovado"
    doubt(root, path)
    (folder / "renders" / "preview.mp4").write_bytes(b"outra previa")
    assert cli.main(["postiz", "schedule", path]) == 1
    client.schedule.assert_not_called()


def test_permission_rule_asks_the_owner_before_schedule() -> None:
    settings = json.loads((Path(__file__).parents[1] / ".claude/settings.json").read_text())
    ask = settings["permissions"]["ask"]
    assert "Bash(* postiz schedule *)" in ask  # vp, .venv/bin/vp e python -m app.cli
    assert not any("pacote" in rule for rule in ask)


def test_schedule_without_doubt_is_refused(
    root: Path, client: Mock, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_payload(root, payload())
    cli.main(["postiz", "pacote", path])
    capsys.readouterr()
    assert cli.main(["postiz", "schedule", path]) == 1
    assert "dúvida cega" in json.loads(capsys.readouterr().err)["error"]
    client.schedule.assert_not_called()


def test_doubt_that_says_stop_blocks_schedule(root: Path, client: Mock) -> None:
    path = write_payload(root, payload())
    cli.main(["postiz", "pacote", path])
    assert doubt(root, path, "não segue", ["canal do YouTube num post de Instagram"]) == 0
    assert cli.main(["postiz", "schedule", path]) == 1
    client.schedule.assert_not_called()
    assert events(root)[-1]["riscos"] == ["canal do YouTube num post de Instagram"]


def test_doubt_must_follow_the_latest_package(root: Path, client: Mock) -> None:
    path = write_payload(root, payload())
    cli.main(["postiz", "pacote", path])
    doubt(root, path)
    cli.main(["postiz", "pacote", path])  # pacote refeito: o parecer anterior não vale para ele
    assert cli.main(["postiz", "schedule", path]) == 1
    client.schedule.assert_not_called()


@pytest.mark.parametrize(
    "report",
    [
        {"veredito": "talvez", "riscos": [], "revisor": "x"},
        {"veredito": "segue", "riscos": [""], "revisor": "x"},
        {"veredito": "segue", "riscos": []},
        ["segue"],
    ],
)
def test_malformed_doubt_is_rejected(root: Path, client: Mock, report: object) -> None:
    path = write_payload(root, payload())
    cli.main(["postiz", "pacote", path])
    (root / "parecer.json").write_text(json.dumps(report), encoding="utf-8")
    assert cli.main(["postiz", "duvida", path, str(root / "parecer.json")]) == 1
    assert events(root)[-1]["event"] == "pacote"


def test_doubt_without_package_is_refused(root: Path, client: Mock) -> None:
    assert doubt(root, write_payload(root, payload())) == 1
    assert not (root / REGISTRO).exists()


def test_doubt_agent_is_read_only() -> None:
    agent = (Path(__file__).parents[1] / ".claude/agents/duvida-cega.md").read_text(encoding="utf-8")
    tools = next(line for line in agent.splitlines() if line.startswith("tools:"))
    assert tools == "tools: Read, Grep, Glob"
