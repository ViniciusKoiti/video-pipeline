"""RF1: a aprovação feita pelo caminho público protege a escrita; a reabertura libera só o alvo (§2.6)."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from app.cli import main
from app.pipeline.constants.numbers_constants import NumbersConstants
from app.pipeline.gates import GateError, gate_report
from app.pipeline.ports import ImmutableManifest
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.reopen import reopen_gate
from app.pipeline.schemas import Asset, Decision, ReviewEntry, SourcesManifest, Status, Step
from app.pipeline.state import compute_input_hash, write_output
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import FIXED_TIME, make_root
from tests.test_gates import EPISODE, SCENES, episode, rendered, stock_asset

Setup = tuple[JsonFileStore, JsonReviewGate, Path]


@pytest.fixture
def ep(tmp_path: Path) -> Setup:
    return episode(tmp_path)


def vp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    """O caminho público: o mesmo `main` do `vp`, numa raiz de projeto isolada."""
    monkeypatch.chdir(make_root(tmp_path))
    return main(list(argv))


def approve(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, step: str, *extra: str) -> None:
    code = vp(tmp_path, monkeypatch, "approve", EPISODE, "--step", step, "--reviewer", "Dono", *extra)
    assert code == 0


def reopen(store: JsonFileStore, review: JsonReviewGate, step: Step, **kw: str) -> ReviewEntry:
    return reopen_gate(
        store, review, EPISODE, step, reviewer="Dono", reason=kw.pop("reason", "fonte nova"),
        now=lambda: datetime.now().astimezone().replace(microsecond=0), **kw,
    )


def refuses(guard: ReviewWriteGuard, name: str, candidate: bytes | None = b'{"mudou": true}') -> bool:
    try:
        guard.check(EPISODE, name, candidate)
    except ImmutableManifest:
        return True
    return False


def test_cli_approval_of_sources_refuses_the_write_before_touching_the_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ep: Setup
) -> None:
    store, review, folder = ep
    approve(tmp_path, monkeypatch, "sources")
    guard = ReviewWriteGuard(store, review)
    before = (folder / "facts.json").read_bytes()
    with pytest.raises(ImmutableManifest, match="gate de sources"):
        manifest = SourcesManifest(episode_id=EPISODE, sources=[])
        write_output(store, EPISODE, "facts.json", manifest, guard=guard)
    assert (folder / "facts.json").read_bytes() == before  # recusou antes de escrever
    assert not refuses(guard, "scenes.json")  # o roteiro ainda não foi aprovado


def test_script_approval_protects_scenes_and_outline_but_not_the_derived_choices(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ep: Setup
) -> None:
    store, review, folder = ep
    (folder / "scenes.json").write_text(SCENES % "null")
    approve(tmp_path, monkeypatch, "script", "--sem-checagem", "teste do gate")
    guard = ReviewWriteGuard(store, review)
    assert refuses(guard, "scenes.json", (SCENES % "null").replace("Fala.", "Outra.").encode())
    assert refuses(guard, "outline.md", b"# outro roteiro\n")
    assert not refuses(guard, "scenes.json", (SCENES % '"pexels-photo-1"').encode())  # gate 3: a imagem
    block = f"{NumbersConstants.BLOCK_START}\nnúmeros\n{NumbersConstants.BLOCK_END}\n"
    assert not refuses(guard, "outline.md", b"# roteiro\n\n" + block.encode())  # bloco gerado do gate 2
    assert refuses(guard, "outline.md", None)  # sem candidato não há exceção


def test_preview_approval_protects_the_stamped_render_and_post_files_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ep: Setup
) -> None:
    store, review, folder = ep
    rendered(folder)
    (folder / "legenda-post.txt").write_text("texto do post")
    approve(tmp_path, monkeypatch, "preview")
    guard = ReviewWriteGuard(store, review)
    assert refuses(guard, "renders/preview.mp4", None) and refuses(guard, "legenda-post.txt", None)
    assert not refuses(guard, "renders/final.mp4", None)  # o final pede nova decisão (#120)
    assert not refuses(guard, "captions.srt", None)  # não existia quando a prévia foi carimbada


def test_approved_asset_protects_the_json_and_the_media_including_reused_ones(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ep: Setup
) -> None:
    store, review, folder = ep
    stock_asset(folder)
    approve(tmp_path, monkeypatch, "assets", "--asset", "pexels-video-1")
    guard = ReviewWriteGuard(store, review)
    assert refuses(guard, "assets/pexels-video-1.json") and refuses(guard, "assets/pexels-video-1.mp4", None)
    assert not refuses(guard, "assets/outro.json")
    reused = stock_asset(folder, "pexels-video-2")
    approved = Asset.model_validate({**reused.model_dump(), "review_status": Status.APPROVED})
    (folder / "assets" / "pexels-video-2.json").write_text(approved.model_dump_json())  # veio aprovado
    with pytest.raises(ImmutableManifest):  # aprovado em outro episódio: o status de topo protege
        store.write(EPISODE, "assets/pexels-video-2.json", reused)


def test_decisions_with_legacy_hash_still_protect_and_a_changed_file_drops_the_approval(ep: Setup) -> None:
    store, review, folder = ep
    legacy = compute_input_hash(
        [folder / "sources.json", folder / "facts.json"], {}, base=store.path(EPISODE, "")
    )
    review.record(EPISODE, ReviewEntry(
        step=Step.SOURCES, decision=Decision.APPROVED, reviewer="Dono", at=FIXED_TIME, input_hash=legacy,
    ))
    guard = ReviewWriteGuard(store, review)
    assert refuses(guard, "facts.json")
    (folder / "facts.json").write_text('{"F1": "editado por fora"}')  # a aprovação caiu, nada a proteger
    assert not refuses(guard, "facts.json")


def test_legacy_script_decision_protects_without_the_derived_exceptions(ep: Setup) -> None:
    store, review, folder = ep
    (folder / "scenes.json").write_text(SCENES % '"pexels-photo-1"')
    whole = compute_input_hash(
        [folder / "scenes.json", folder / "outline.md"], {}, base=store.path(EPISODE, "")
    )
    review.record(EPISODE, ReviewEntry(
        step=Step.SCRIPT, decision=Decision.APPROVED, reviewer="Dono", at=FIXED_TIME, input_hash=whole,
    ))
    guard = ReviewWriteGuard(store, review)
    assert refuses(guard, "scenes.json", (SCENES % '"outra-imagem"').encode())  # decisão antiga: sem exceção
    assert refuses(guard, "outline.md", b"# roteiro mudou\n")


def test_reopen_releases_only_the_target_keeps_history_and_records_who_and_why(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ep: Setup
) -> None:
    store, review, folder = ep
    (folder / "scenes.json").write_text(SCENES % "null")
    approve(tmp_path, monkeypatch, "sources")
    approve(tmp_path, monkeypatch, "script", "--sem-checagem", "teste")
    old = review.log(EPISODE).entries
    entry = reopen(store, review, Step.SOURCES, reason="fonte nova do jornal")
    guard = ReviewWriteGuard(store, review)
    assert not refuses(guard, "facts.json") and not refuses(guard, "sources.json")
    assert refuses(guard, "scenes.json")  # o roteiro continua carimbado
    entries = review.log(EPISODE).entries
    assert entries[: len(old)] == old and entries[-1] == entry  # só acrescenta
    assert (entry.reviewer, entry.decision) == ("Dono", Decision.CHANGES_REQUESTED)
    assert entry.notes == "reaberta: fonte nova do jornal"
    [row] = [r for r in gate_report(store, review, EPISODE) if r.step is Step.SOURCES]
    assert row.entry == entry
    approve(tmp_path, monkeypatch, "sources")  # reaprovar volta a proteger
    assert refuses(guard, "facts.json")


@pytest.mark.parametrize("skew", [timedelta(0), timedelta(hours=-1)], ids=["same-second", "clock-went-back"])
def test_the_reopen_wins_even_with_the_same_or_an_earlier_timestamp(ep: Setup, skew: timedelta) -> None:
    store, review, _ = ep
    stamped = [store.path(EPISODE, n) for n in ("sources.json", "facts.json")]
    review.record(EPISODE, ReviewEntry(
        step=Step.SOURCES, decision=Decision.APPROVED, reviewer="Dono", at=FIXED_TIME,
        input_hash=compute_input_hash(stamped, {}, base=store.path(EPISODE, "")),
    ))
    when = FIXED_TIME + skew
    reopen_gate(store, review, EPISODE, Step.SOURCES, reviewer="Dono", reason="x", now=lambda: when)
    latest = review.log(EPISODE).latest(Step.SOURCES)
    assert latest is not None and latest.decision is Decision.CHANGES_REQUESTED
    assert not refuses(ReviewWriteGuard(store, review), "facts.json")  # a ordem do log manda, não o relógio


@pytest.mark.parametrize(
    ("step", "kwargs", "message"),
    [
        (Step.SOURCES, {"reason": "  "}, "motivo"),
        (Step.SOURCES, {}, "não está aprovado"),
        (Step.VOICE, {}, "não tem gate"),
        (Step.ASSETS, {}, "ativo por ativo"),
        (Step.SOURCES, {"asset_id": "x"}, "ativo por ativo"),
    ],
)
def test_reopen_refuses_what_it_cannot_reopen(
    ep: Setup, step: Step, kwargs: dict[str, str], message: str
) -> None:
    store, review, _ = ep
    with pytest.raises(GateError, match=message):
        reopen(store, review, step, **kwargs)
    assert review.log(EPISODE).entries == []


def test_reopening_an_asset_releases_its_json_and_media(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, ep: Setup
) -> None:
    store, review, folder = ep
    stock_asset(folder)
    approve(tmp_path, monkeypatch, "assets", "--asset", "pexels-video-1")
    guard = ReviewWriteGuard(store, review)
    assert refuses(guard, "assets/pexels-video-1.json")
    reopen(store, review, Step.ASSETS, asset_id="pexels-video-1", reason="troca de enquadramento")
    asset = store.read(EPISODE, "assets/pexels-video-1.json", Asset)
    assert asset.review_status is Status.NEEDS_REVIEW  # o que a aprovação tinha refletido
    store.write(EPISODE, "assets/pexels-video-1.json", asset)  # o código volta a poder escrever
    assert not refuses(guard, "assets/pexels-video-1.json")
    assert not refuses(guard, "assets/pexels-video-1.mp4", None)


def test_vp_reopen_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], ep: Setup
) -> None:
    store, review, folder = ep
    approve(tmp_path, monkeypatch, "sources")
    base: Callable[..., int] = lambda *a: vp(tmp_path, monkeypatch, "reopen", EPISODE, *a)  # noqa: E731
    with pytest.raises(SystemExit):  # --reason é obrigatório
        base("--step", "sources", "--reviewer", "Dono")
    capsys.readouterr()
    assert base("--step", "sources", "--reviewer", "Dono", "--reason", "  ") == 1
    assert "motivo" in capsys.readouterr().err
    assert base("--step", "sources", "--reviewer", "Dono", "--reason", "fonte nova") == 0
    assert "reaberto: sources por Dono" in capsys.readouterr().out
    assert base("--step", "sources", "--reviewer", "Dono", "--reason", "de novo") == 1  # já não está aprovado
    log = json.loads((folder / "review.json").read_text())
    assert [e["decision"] for e in log["entries"]] == ["approved", "changes_requested"]
    assert log["entries"][1]["notes"] == "reaberta: fonte nova"
    assert not refuses(ReviewWriteGuard(store, review), "facts.json")
