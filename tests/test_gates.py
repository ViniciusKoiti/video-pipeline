"""Gates humanos por comando (vp approve, vp reject, vp status): o que se carimba e quando a decisão vale."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.cli import main
from app.pipeline.gates import GateError, gate_hash, gate_report, record_decision
from app.pipeline.schemas import Asset, Decision, Status, Step
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import FIXED_TIME, make_root

EPISODE = "ep-teste"


def episode(tmp_path: Path) -> tuple[JsonFileStore, JsonReviewGate, Path]:
    store = JsonFileStore(tmp_path / "data" / "episodes")
    folder = store.path(EPISODE, "")
    (folder / "assets").mkdir(parents=True)
    for name, text in {
        "sources.json": "{}", "facts.json": "{}", "scenes.json": "{}", "outline.md": "# roteiro\n"
    }.items():
        (folder / name).write_text(text)
    return store, JsonReviewGate(store), folder


def stock_asset(folder: Path, asset_id: str = "pexels-video-1", *, usage_notes: str = "conferido") -> Asset:
    media = folder / "assets" / f"{asset_id}.mp4"
    media.write_bytes(b"video")
    asset = Asset(
        id=asset_id,
        provider="pexels",
        provider_id="1",
        original_url="https://example.org/1.mp4",
        page_url="https://example.org/video/1",
        author="Fulano",
        license_id="Pexels",
        attribution_text="Fulano via Pexels",
        usage_notes=usage_notes,
        retrieved_at=FIXED_TIME,
        sha256=hashlib.sha256(b"video").hexdigest(),
        review_status=Status.NEEDS_REVIEW,
    )
    (folder / "assets" / f"{asset_id}.json").write_text(asset.model_dump_json(indent=2))
    return asset


def decide(store: JsonFileStore, review: JsonReviewGate, step: Step, decision: Decision, **kw: str) -> None:
    record_decision(store, review, EPISODE, step, decision, reviewer="Dono", now=lambda: FIXED_TIME, **kw)


def test_gate_1_stamps_sources_and_facts(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    before = gate_hash(store, EPISODE, Step.SOURCES)
    (folder / "scenes.json").write_text('{"outro": 1}')
    assert gate_hash(store, EPISODE, Step.SOURCES) == before  # o roteiro não faz parte do gate 1
    (folder / "facts.json").write_text('{"F1": "mudou"}')
    assert gate_hash(store, EPISODE, Step.SOURCES) != before


def test_decision_is_valid_until_the_content_changes(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    decide(store, review, Step.SCRIPT, Decision.APPROVED)
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.SCRIPT]
    assert row.entry is not None and row.entry.reviewer == "Dono" and row.valid
    (folder / "outline.md").write_text("# roteiro mudou\n")
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.SCRIPT]
    assert not row.valid


def test_approving_an_asset_reflects_review_status(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    stock_asset(folder)
    decide(store, review, Step.ASSETS, Decision.APPROVED, asset_id="pexels-video-1")
    saved = Asset.model_validate_json((folder / "assets" / "pexels-video-1.json").read_text())
    assert saved.review_status is Status.APPROVED
    [entry] = review.log(EPISODE).entries
    assert entry.input_hash == f"sha256:{saved.sha256}" and entry.asset_id == "pexels-video-1"
    with pytest.raises(GateError, match="já está aprovado"):
        decide(store, review, Step.ASSETS, Decision.APPROVED, asset_id="pexels-video-1")


def test_asset_without_rights_check_is_refused_and_nothing_is_recorded(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    stock_asset(folder, usage_notes="")
    with pytest.raises(GateError, match="conferência de pessoas, marcas e texto"):
        decide(store, review, Step.ASSETS, Decision.APPROVED, asset_id="pexels-video-1")
    assert review.log(EPISODE).entries == []


def test_asset_whose_file_changed_is_refused(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    stock_asset(folder)
    (folder / "assets" / "pexels-video-1.mp4").write_bytes(b"outro video")
    with pytest.raises(GateError, match="não bate com o sha256"):
        decide(store, review, Step.ASSETS, Decision.APPROVED, asset_id="pexels-video-1")


def test_rejected_and_removed_asset_is_not_pending(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    stock_asset(folder)
    decide(store, review, Step.ASSETS, Decision.REJECTED, asset_id="pexels-video-1", notes="marca visível")
    for suffix in (".mp4", ".json"):
        (folder / "assets" / f"pexels-video-1{suffix}").unlink()
    [row] = [r for r in gate_report(store, review, EPISODE) if r.asset_id]
    assert row.entry is not None and row.entry.decision is Decision.REJECTED and row.current_hash is None


def test_asset_flag_only_for_assets_step(tmp_path: Path) -> None:
    store, _, _ = episode(tmp_path)
    with pytest.raises(GateError, match="--asset só vale"):
        gate_hash(store, EPISODE, Step.SCRIPT, "pexels-video-1")
    with pytest.raises(GateError, match="informe --asset"):
        gate_hash(store, EPISODE, Step.ASSETS)
    with pytest.raises(GateError, match="ainda não tem gate"):
        gate_hash(store, EPISODE, Step.VOICE)


# --- CLI ----------------------------------------------------------------------------------------


def run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    monkeypatch.chdir(make_root(tmp_path))
    return main(list(argv))


def test_cli_approve_reject_and_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _, _, folder = episode(tmp_path)
    stock_asset(folder)
    assert run(tmp_path, monkeypatch, "approve", EPISODE, "--step", "sources", "--reviewer", "Dono") == 0
    assert run(tmp_path, monkeypatch, "reject", EPISODE, "--step", "script", "--reviewer", "Dono",
               "--reason", "gancho sem imagem", "--changes") == 0
    args = ("approve", EPISODE, "--step", "assets", "--asset", "pexels-video-1", "--reviewer", "Dono")
    assert run(tmp_path, monkeypatch, *args) == 0
    capsys.readouterr()
    assert run(tmp_path, monkeypatch, "status", EPISODE) == 0
    out = capsys.readouterr().out
    assert "gate  sources" in out and "aprovado" in out and "vale" in out
    assert "mudanças pedidas" in out
    assert out.strip().endswith("pendências: script")
    log = json.loads((folder / "review.json").read_text())
    assert [e["decision"] for e in log["entries"]] == ["approved", "changes_requested", "approved"]
    assert log["entries"][1]["notes"] == "gancho sem imagem"


def test_cli_reports_gate_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    episode(tmp_path)
    assert run(tmp_path, monkeypatch, "approve", EPISODE, "--step", "assets", "--reviewer", "Dono") == 1
    assert "informe --asset" in capsys.readouterr().err
