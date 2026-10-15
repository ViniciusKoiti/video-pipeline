import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from app import cli
from app.bootstrap import ConfigurationError
from app.commands import postiz as postiz_command
from app.providers.errors import ProviderError
from tests.fakes import make_root


@pytest.fixture
def postiz(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Mock:
    monkeypatch.chdir(make_root(tmp_path))
    client = Mock()
    monkeypatch.setattr(postiz_command, "build_postiz", Mock(return_value=client))
    return client


@pytest.mark.parametrize("argv", [["postiz", "--help"], ["postiz", "schedule", "--help"]])
def test_help_does_not_load_credentials(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> None:
    context = Mock(side_effect=AssertionError("help não precisa de configuração"))
    monkeypatch.setattr(cli, "build_context", context)
    with pytest.raises(SystemExit) as exc:
        cli.main(argv)
    assert exc.value.code == 0
    context.assert_not_called()


def test_integrations_outputs_json(postiz: Mock, capsys: pytest.CaptureFixture[str]) -> None:
    postiz.integrations.return_value = [{"id": "instagram-1", "name": "Nabote — Histórias"}]
    assert cli.main(["postiz", "integrations"]) == 0
    output = capsys.readouterr()
    assert json.loads(output.out) == postiz.integrations.return_value
    assert "Histórias" in output.out
    assert output.err == ""


@pytest.mark.parametrize("argv", [["postiz"], ["postiz", "posts"], ["postiz", "posts", "--start", "2026"]])
def test_subcommand_and_post_interval_are_required(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(argv)
    assert exc.value.code == 2


def test_schedule_reads_native_payload(
    postiz: Mock, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    payload = {
        "type": "schedule",
        "date": "2026-10-15T15:30:00.000Z",
        "posts": [{"integration": {"id": "instagram-1"}, "value": [{"content": "Nabote: fé"}]}],
    }
    path = tmp_path / "schedule.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    postiz.schedule.return_value = [{"postId": "post-1"}]
    assert cli.main(["postiz", "schedule", str(path)]) == 0
    postiz.schedule.assert_called_once_with(payload)
    assert json.loads(capsys.readouterr().out) == [{"postId": "post-1"}]


def test_upload_passes_path(postiz: Mock, capsys: pytest.CaptureFixture[str]) -> None:
    postiz.upload.return_value = {"id": "media-1", "path": "https://example.test/video.mp4"}
    assert cli.main(["postiz", "upload", "video.mp4"]) == 0
    postiz.upload.assert_called_once_with(Path("video.mp4"))
    assert json.loads(capsys.readouterr().out) == postiz.upload.return_value


def test_configuration_error_is_json_without_secret(
    postiz: Mock, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        postiz_command, "build_postiz", Mock(side_effect=ConfigurationError("secret-api-key"))
    )
    assert cli.main(["postiz", "integrations"]) == 1
    output = capsys.readouterr()
    assert "POSTIZ_API_KEY" in json.loads(output.err)["error"]
    assert "secret-api-key" not in output.err
    assert "Traceback" not in output.err
    assert output.out == ""
    postiz.integrations.assert_not_called()


def test_invalid_project_configuration_does_not_expose_environment_secret(
    postiz: Mock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    config = tmp_path / "config/providers.toml"
    config.write_text(config.read_text().replace("[workers_ai]", "[unconfigured_workers_ai]"))
    monkeypatch.setenv("POSTIZ_API_KEY", "private-environment-sentinel")
    assert cli.main(["postiz", "integrations"]) == 1
    output = capsys.readouterr()
    assert json.loads(output.err)["error"]
    assert "private-environment-sentinel" not in output.err
    assert "Traceback" not in output.err
    assert output.out == ""
    postiz.integrations.assert_not_called()


def test_missing_project_root_is_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    assert cli.main(["postiz", "integrations"]) == 1
    output = capsys.readouterr()
    assert json.loads(output.err)["error"]
    assert output.out == ""


def test_provider_error_is_json(postiz: Mock, capsys: pytest.CaptureFixture[str]) -> None:
    postiz.integrations.side_effect = ProviderError("postiz", "HTTP 401: autorização recusada")
    assert cli.main(["postiz", "integrations"]) == 1
    output = capsys.readouterr()
    assert json.loads(output.err) == {"error": "postiz: HTTP 401: autorização recusada"}
    assert output.out == ""


@pytest.mark.parametrize("file_content", ["private-input-that-is-not-json", None])
def test_unreadable_or_invalid_payload_is_safe_json(
    file_content: str | None,
    postiz: Mock,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "schedule.json"
    if file_content is not None:
        path.write_text(file_content, encoding="utf-8")
    assert cli.main(["postiz", "schedule", str(path)]) == 1
    output = capsys.readouterr()
    assert json.loads(output.err)["error"]
    assert "private-input" not in output.err
    assert output.out == ""
    postiz.schedule.assert_not_called()


def test_factory_receives_dotenv_settings_from_root(
    postiz: Mock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("POSTIZ_API_KEY", raising=False)
    (tmp_path / ".env").write_text("POSTIZ_API_KEY=offline-test-token\n", encoding="utf-8")
    folder = tmp_path / "data" / "episodes"
    folder.mkdir(parents=True)
    monkeypatch.chdir(folder)
    postiz.integrations.return_value = []
    assert cli.main(["postiz", "integrations"]) == 0
    settings = postiz_command.build_postiz.call_args.args[0]
    assert settings.data_dir == tmp_path / "data"
    assert settings.secrets.postiz_api_key.get_secret_value() == "offline-test-token"
    assert json.loads(capsys.readouterr().out) == []
