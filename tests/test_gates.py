"""Gates humanos por comando (vp approve, vp reject, vp status): o que se carimba e quando a decisão vale."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.cli import main
from app.pipeline.gates import (
    GateError,
    GateStatus,
    gate_hash,
    gate_report,
    latest_check,
    missing_pieces,
    record_check,
    record_decision,
)
from app.pipeline.schemas import (
    Asset,
    CheckVerdict,
    Decision,
    EpisodeFormat,
    EpisodeManifest,
    EpisodeScene,
    ReviewEntry,
    Status,
    Step,
    VideoSpec,
)
from app.pipeline.state import compute_input_hash
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


def checked(store: JsonFileStore, verdict: CheckVerdict = CheckVerdict.APPROVED, *problems: str) -> None:
    record_check(store, EPISODE, verdict, list(problems), reviewer="verificador", now=lambda: FIXED_TIME)


def test_decision_is_valid_until_the_content_changes(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    checked(store)
    decide(store, review, Step.SCRIPT, Decision.APPROVED)
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.SCRIPT]
    assert row.entry is not None and row.entry.reviewer == "Dono" and row.valid
    (folder / "outline.md").write_text("# roteiro mudou\n")
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.SCRIPT]
    assert not row.valid


SCENES = '{"scenes": [{"id": "S01", "narration": "Fala.", "shots": [{"anchor": "Fala", "asset_id": %s}]}]}'


def script_row(store: JsonFileStore, review: JsonReviewGate) -> GateStatus:
    return next(r for r in gate_report(store, review, EPISODE) if r.step is Step.SCRIPT)


def test_choosing_an_image_keeps_the_script_decision_and_the_check(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    (folder / "scenes.json").write_text(SCENES % "null")
    checked(store)
    decide(store, review, Step.SCRIPT, Decision.APPROVED)
    (folder / "scenes.json").write_text(SCENES % '"pexels-photo-1"')  # a imagem é do gate 3 (§5)
    assert script_row(store, review).valid and latest_check(store, EPISODE)[1]
    (folder / "scenes.json").write_text((SCENES % '"pexels-photo-1"').replace("Fala.", "Fala nova."))
    assert not script_row(store, review).valid and not latest_check(store, EPISODE)[1]


def test_decisions_stamped_with_the_whole_file_still_hold(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    (folder / "scenes.json").write_text(SCENES % '"pexels-photo-1"')
    whole = compute_input_hash(
        [folder / "scenes.json", folder / "outline.md"], {}, base=store.path(EPISODE, "")
    )
    assert gate_hash(store, EPISODE, Step.SCRIPT) != whole
    review.record(
        EPISODE,
        ReviewEntry(
            step=Step.SCRIPT, decision=Decision.APPROVED, reviewer="Dono", at=FIXED_TIME, input_hash=whole
        ),
    )
    assert script_row(store, review).valid  # decisão gravada antes desta regra
    (folder / "outline.md").write_text("# roteiro mudou\n")
    assert not script_row(store, review).valid


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
    assert out.strip().endswith("pendências: script, preview")  # sem render ainda
    log = json.loads((folder / "review.json").read_text())
    assert [e["decision"] for e in log["entries"]] == ["approved", "changes_requested", "approved"]
    assert log["entries"][1]["notes"] == "gancho sem imagem"


def test_cli_reports_gate_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    episode(tmp_path)
    assert run(tmp_path, monkeypatch, "approve", EPISODE, "--step", "assets", "--reviewer", "Dono") == 1
    assert "informe --asset" in capsys.readouterr().err


def rendered(folder: Path, name: str = "preview.mp4", content: bytes = b"previa") -> Path:
    (folder / "renders").mkdir(exist_ok=True)
    (folder / "renders" / name).write_bytes(content)
    return folder / "renders" / name


def test_preview_gate_needs_a_render(tmp_path: Path) -> None:
    store, review, _ = episode(tmp_path)
    with pytest.raises(GateError, match="nenhum render"):
        decide(store, review, Step.PREVIEW, Decision.APPROVED)
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.PREVIEW]
    assert row.entry is None and row.current_hash is None


def test_preview_gate_covers_render_captions_and_post_text(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    rendered(folder)
    before = gate_hash(store, EPISODE, Step.PREVIEW)
    (folder / "captions.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nOlá.\n")
    with_captions = gate_hash(store, EPISODE, Step.PREVIEW)
    assert with_captions != before
    (folder / "legenda-post.txt").write_text("Salve para lembrar.\n")
    assert gate_hash(store, EPISODE, Step.PREVIEW) != with_captions


def test_the_final_render_reopens_an_approved_preview(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    rendered(folder)
    decide(store, review, Step.PREVIEW, Decision.APPROVED)
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.PREVIEW]
    assert row.valid
    rendered(folder, "final.mp4", b"final com voz final")
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.PREVIEW]
    assert not row.valid  # a versão final é revista de novo


def _episode_json(folder: Path, *, portrait: bool, captions: str | None) -> None:
    scene = EpisodeScene.model_validate(
        {"id": "S01", "start_ms": 0, "duration_ms": 1000, "narration": "Olá.", "audio": "voice/S01.wav",
         "shots": [{"start_ms": 0, "duration_ms": 1000,
                    "spec": {"kind": "keyword", "text": "Olá", "anchor": "Olá"}}]}
    )
    manifest = EpisodeManifest(
        schema_version=2, episode_id=EPISODE, title="teste", language="pt-BR", format=EpisodeFormat.EXPLAINER,
        scenes=[scene], video=VideoSpec.for_orientation("portrait" if portrait else "landscape"),
        captions=captions,
    )
    (folder / "episode.json").write_text(manifest.model_dump_json())


def test_missing_captions_are_pending_only_in_portrait(tmp_path: Path) -> None:
    store, _, folder = episode(tmp_path)
    assert missing_pieces(store, EPISODE) == []  # sem episode.json ainda
    _episode_json(folder, portrait=True, captions=None)
    assert missing_pieces(store, EPISODE) == ["legenda (captions.srt)"]
    _episode_json(folder, portrait=True, captions="captions.srt")
    assert missing_pieces(store, EPISODE) == ["legenda (captions.srt)"]  # o arquivo ainda não existe
    (folder / "captions.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nOlá.\n")
    assert missing_pieces(store, EPISODE) == []
    _episode_json(folder, portrait=False, captions=None)
    assert missing_pieces(store, EPISODE) == []


def test_gate_2_needs_a_current_approving_check(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    with pytest.raises(GateError, match="parecer do verificador"):
        decide(store, review, Step.SCRIPT, Decision.APPROVED)
    checked(store, CheckVerdict.REJECTED, "DIVERGE S03 ano")
    with pytest.raises(GateError, match="parecer do verificador"):
        decide(store, review, Step.SCRIPT, Decision.APPROVED)
    checked(store)
    (folder / "facts.json").write_text('{"F1": "ficha mudou depois do parecer"}')
    entry, valid = latest_check(store, EPISODE)
    assert entry is not None and not valid
    with pytest.raises(GateError, match="parecer do verificador"):
        decide(store, review, Step.SCRIPT, Decision.APPROVED)
    decide(store, review, Step.SCRIPT, Decision.CHANGES_REQUESTED)  # pedir mudança não precisa de parecer


def test_gate_2_without_check_records_the_owner_reason(tmp_path: Path) -> None:
    store, review, _ = episode(tmp_path)
    reason = "roteiro de teste, sem fatos"
    decide(store, review, Step.SCRIPT, Decision.APPROVED, notes="ok", skip_check=reason)
    entry = review.log(EPISODE).latest(Step.SCRIPT)
    assert entry is not None and entry.notes == "ok; sem checagem: roteiro de teste, sem fatos"
    with pytest.raises(GateError):
        decide(store, review, Step.SCRIPT, Decision.APPROVED, skip_check="   ")


def test_cli_checagem_records_and_status_shows_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _, _, folder = episode(tmp_path)
    report = tmp_path / "parecer.json"
    report.write_text(json.dumps({"verdict": "approved", "problems": []}))
    assert run(tmp_path, monkeypatch, "approve", EPISODE, "--step", "script", "--reviewer", "Dono") == 1
    assert "parecer do verificador" in capsys.readouterr().err
    assert run(tmp_path, monkeypatch, "checagem", EPISODE, str(report)) == 0
    log = json.loads((folder / "checagem.json").read_text())
    assert [e["verdict"] for e in log["entries"]] == ["approved"]
    assert run(tmp_path, monkeypatch, "approve", EPISODE, "--step", "script", "--reviewer", "Dono") == 0
    capsys.readouterr()
    run(tmp_path, monkeypatch, "status", EPISODE)
    assert "verificador" in capsys.readouterr().out
    report.write_text(json.dumps({"verdict": "talvez"}))
    assert run(tmp_path, monkeypatch, "checagem", EPISODE, str(report)) == 1
