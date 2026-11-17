"""Emenda de 2026-11-09 da ADR 007 (e ADR 001, item 5): clipe animado do projeto como ativo `Original`.

O modelo aceita `media: clip` com a licença Original (provider original, origin e usage_notes) e
`vp assets original` registra o `.mp4` sem banco nem rede. Aprovado nunca é alterado; mídia nova de um
ativo não aprovado refaz a entrada.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.pipeline.assets import AssetError, AssetIntake
from app.pipeline.file_hash import sha256_file
from app.pipeline.models.intake_action import IntakeAction
from app.pipeline.models.provider import Provider
from app.pipeline.models.status import Status
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.schemas import Asset
from app.storage.json_files import JsonFileStore, JsonReviewGate

EP = "ep-original"
NOW = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)
ORIGIN = "video/src/previews/mec-fechadura-pt/index.tsx#FechaduraS20 (variant=limpo)"
NOTES = "limpo, 212 quadros a 30 fps; sem pessoa, marca nem texto de terceiros (conferido nos quadros)"


def original_clip(**kw: object) -> Asset:
    base = {
        "id": "mec-s20",
        "provider": Provider.ORIGINAL,
        "provider_id": "mec-s20",
        "license_id": "Original",
        "origin": ORIGIN,
        "usage_notes": NOTES,
        "media": "clip",
        "retrieved_at": NOW,
        "review_status": Status.NEEDS_REVIEW,
    }
    return Asset.model_validate({**base, **kw})


def approved(asset: Asset, sha256: str = "a" * 64) -> dict[str, object]:
    return {**asset.model_dump(), "review_status": Status.APPROVED, "sha256": sha256}


# --- Modelo ---------------------------------------------------------------------------------------


def test_an_original_clip_with_origin_and_notes_can_be_approved() -> None:
    clip = Asset.model_validate(approved(original_clip()))
    assert (clip.media, clip.license_id, clip.review_status) == ("clip", "Original", Status.APPROVED)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"origin": None}, "origin"),
        ({"origin": "  "}, "origin"),
        ({"usage_notes": ""}, "usage_notes"),
        ({"timecode": "00:00:01-00:00:02"}, "timecode"),
        ({"provider": Provider.PEXELS, "page_url": "https://example.org/x"}, "provider original"),
    ],
)
def test_an_original_clip_missing_its_proof_cannot_be_approved(
    change: dict[str, object], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        Asset.model_validate(approved(original_clip(**change)))


def test_a_clip_is_still_refused_for_the_other_licenses_and_a_cited_clip_still_needs_its_timecode() -> None:
    stock = {
        "provider": Provider.PEXELS,
        "license_id": "Pexels",
        "author": "F",
        "attribution_text": "F via Pexels",
    }
    with pytest.raises(ValidationError, match="clipe só na licença Citacao"):
        Asset.model_validate(approved(original_clip(**stock, page_url="https://example.org/1")))
    cited = {
        "provider": Provider.OWNER_CAPTURE,
        "license_id": "Citacao",
        "work": "Obra",
        "attribution_text": "Crédito",
    }
    with pytest.raises(ValidationError, match="timecode"):
        Asset.model_validate(approved(original_clip(**cited)))


def test_an_original_still_keeps_working_as_before() -> None:
    still = Asset.model_validate(approved(original_clip(media="still", origin=None)))
    assert still.media == "still"


# --- Entrada --------------------------------------------------------------------------------------


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.store = JsonFileStore(tmp_path / "episodes")
        self.review = JsonReviewGate(self.store)
        self.intake = AssetIntake(self.store, ReviewWriteGuard(self.store, self.review))
        self.source = tmp_path / "S20.mp4"
        self.source.write_bytes(b"CLIPE-V1")

    def register(self, scene: str = "S20", source: Path | None = None):  # noqa: ANN202
        return self.intake.register_local(EP, original_clip(), scene, source or self.source)

    def asset(self) -> Asset:
        return self.store.read(EP, "assets/mec-s20.json", Asset)

    def media(self) -> Path:
        return self.store.path(EP, "assets/mec-s20.mp4")


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


def test_a_new_clip_is_copied_with_its_hash_and_scene_and_stays_unapproved(env: Env) -> None:
    result = env.register()
    assert result.action is IntakeAction.DOWNLOADED
    stored = env.asset()
    assert (stored.used_in_scenes, stored.review_status, stored.media) == (
        ["S20"],
        Status.NEEDS_REVIEW,
        "clip",
    )
    assert stored.sha256 == sha256_file(env.source) == sha256_file(env.media())
    assert env.source.read_bytes() == b"CLIPE-V1"  # a origem não é tocada


def test_the_same_clip_for_another_scene_keeps_the_first_and_repeating_is_idempotent(env: Env) -> None:
    env.register("S20")
    assert env.register("S21").action is IntakeAction.SCENE_ADDED
    before = env.store.path(EP, "assets/mec-s20.json").read_bytes()
    assert env.register("S21").action is IntakeAction.UNCHANGED
    assert env.store.path(EP, "assets/mec-s20.json").read_bytes() == before
    assert env.asset().used_in_scenes == ["S20", "S21"]


def test_a_new_render_of_an_unapproved_clip_replaces_the_media_and_keeps_the_scenes(env: Env) -> None:
    env.register("S20")
    env.source.write_bytes(b"CLIPE-V2")
    assert env.register("S21").action is IntakeAction.REPAIRED
    assert env.media().read_bytes() == b"CLIPE-V2"
    assert (env.asset().used_in_scenes, env.asset().sha256) == (["S20", "S21"], sha256_file(env.source))


def test_an_approved_clip_is_never_touched_and_a_different_render_is_an_explicit_error(env: Env) -> None:
    env.register("S20")
    path = env.store.path(EP, "assets/mec-s20.json")
    path.write_text(
        Asset.model_validate(approved(env.asset(), env.asset().sha256 or "")).model_dump_json(indent=2)
    )
    before = path.read_bytes()
    assert env.register("S21").action is IntakeAction.APPROVED_UNTOUCHED
    assert path.read_bytes() == before
    env.source.write_bytes(b"CLIPE-V2")
    with pytest.raises(AssetError, match="vp reopen --step assets --asset mec-s20"):
        env.register("S21")
    assert env.media().read_bytes() == b"CLIPE-V1"


def test_only_an_existing_non_empty_mp4_is_accepted(env: Env, tmp_path: Path) -> None:
    empty, wrong, missing = tmp_path / "vazio.mp4", tmp_path / "clipe.webm", tmp_path / "nao-existe.mp4"
    empty.write_bytes(b"")
    wrong.write_bytes(b"x")
    for source in (empty, wrong, missing):
        with pytest.raises(AssetError, match="precisa ser um .mp4"):
            env.register(source=source)
    assert not env.store.path(EP, "assets").exists()  # nada foi criado


# --- Comando --------------------------------------------------------------------------------------


def run(tmp_path: Path, *argv: str) -> int:
    args = build_parser().parse_args(["assets", *argv])
    store = JsonFileStore(tmp_path / "episodes")
    context = SimpleNamespace(
        store=store, review=JsonReviewGate(store), settings=SimpleNamespace(data_dir=tmp_path)
    )
    return handled("vp assets", lambda: HANDLERS["assets"](args, context))  # type: ignore[arg-type]


def test_the_command_registers_a_clip_without_any_bank(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = run(
        tmp_path,
        "original",
        EP,
        "S20",
        str(env.source),
        "--asset-id",
        "mec-s20",
        "--composicao",
        ORIGIN,
        "--notas",
        NOTES,
    )
    assert code == 0
    assert "mec-s20: baixado; cenas ['S20']" in capsys.readouterr().out
    stored = env.asset()
    assert (stored.provider, stored.license_id, stored.media, stored.origin) == (
        Provider.ORIGINAL,
        "Original",
        "clip",
        ORIGIN,
    )
    assert stored.sha256 == sha256_file(env.media())


def test_the_command_refuses_empty_proof_and_a_bad_file_with_a_message(
    env: Env, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    common = ("original", EP, "S20", str(env.source), "--asset-id", "mec-s20")
    assert run(tmp_path, *common, "--composicao", " ", "--notas", NOTES) == 1
    assert run(tmp_path, *common, "--composicao", ORIGIN, "--notas", "") == 1
    err = capsys.readouterr().err
    assert err.count("não podem ser vazios") == 2
    bad = (
        "original",
        EP,
        "S20",
        str(tmp_path / "x.webm"),
        "--asset-id",
        "mec-s20",
        "--composicao",
        ORIGIN,
        "--notas",
        NOTES,
    )
    assert run(tmp_path, *bad) == 1
    assert "precisa ser um .mp4" in capsys.readouterr().err
    assert not env.store.path(EP, "assets").exists()
