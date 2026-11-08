"""RF5 (música): o catálogo não substitui faixa e a entrada no episódio confere o arquivo e não troca nada."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.pipeline.file_hash import sha256_file
from app.pipeline.models.audio_probe import AudioProbe
from app.pipeline.models.track_draft import TrackDraft
from app.pipeline.models.track_install_action import TrackInstallAction
from app.pipeline.music import MusicCatalogError, load_music_catalog
from app.pipeline.music_library import add_track, install_track, slug
from app.pipeline.ports import EpisodeLocked
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.schemas import Asset, Decision, ReviewEntry, Status, Step
from app.storage.json_files import JsonFileStore, JsonReviewGate

EP = "ep-musica"
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
PROBE = AudioProbe(duration_ms=lambda path: 61_000, lufs=lambda path: -18.0, intensity=lambda lufs: 3)


def draft(title: str = "Alias", **over: object) -> TrackDraft:
    base = {
        "title": title,
        "moods": ("calmo", "foco"),
        "vocals": False,
        "license_id": "YouTube-Audio-Library",
    }
    return TrackDraft(**{**base, **over})  # type: ignore[arg-type]


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.data = tmp_path / "data"
        self.music = self.data / "music"
        self.store = JsonFileStore(self.data / "episodes")
        self.review = JsonReviewGate(self.store)
        self.guard = ReviewWriteGuard(self.store, self.review)
        self.store.path(EP, "").mkdir(parents=True)
        self.source = tmp_path / "Alias - Fulano.mp3"
        self.source.write_bytes(b"ID3-audio-bytes")

    def add(self, title: str = "Alias", **over: object):  # noqa: ANN202
        return add_track(self.music, self.source, draft(title, **over), PROBE, NOW)

    def install(self, asset_id: str = "ytal-alias") -> TrackInstallAction:
        return install_track(self.store, self.guard, self.music, EP, asset_id)

    def assets(self) -> list[str]:
        folder = self.store.path(EP, "assets")
        return sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


def test_slug_makes_an_ascii_id() -> None:
    assert (
        slug("Spirit of Fire!") == "spirit-of-fire"
        and slug("Água de Coco") == "agua-de-coco"
        and slug("♪♪") == ""
    )


# --- Adicionar ao catálogo ----------------------------------------------------------------------


def test_adding_a_track_writes_the_media_the_asset_and_the_catalog(env: Env) -> None:
    track, lufs = env.add(artist="Fulano")
    assert (track.asset_id, track.file, track.duration_ms, track.intensity, lufs) == (
        "ytal-alias",
        "ytal-alias.mp3",
        61_000,
        3,
        -18.0,
    )
    asset = Asset.model_validate_json((env.music / "ytal-alias.json").read_text())
    assert asset.sha256 == sha256_file(env.music / "ytal-alias.mp3") and asset.author == "Fulano"
    assert "Voz cantada: não" in asset.usage_notes and asset.license_id == "YouTube-Audio-Library"
    assert [t.asset_id for t in load_music_catalog(env.data).tracks] == ["ytal-alias"]  # type: ignore[union-attr]


def test_a_track_already_in_the_catalog_is_never_replaced(env: Env) -> None:
    env.add()
    before = {p.name: p.read_bytes() for p in env.music.iterdir()}
    env.source.write_bytes(b"outro audio com o mesmo titulo")
    with pytest.raises(MusicCatalogError, match="ytal-alias já está no catálogo"):
        env.add()
    assert {p.name: p.read_bytes() for p in env.music.iterdir()} == before


@pytest.mark.parametrize(
    ("over", "match"),
    [
        ({"license_id": "CC-BY-SA-4.0"}, "licença 'CC-BY-SA-4.0' fora de"),
        ({"license_id": "CC-BY-4.0"}, "faixa CC exige a atribuição"),
        ({"license_id": "CC-BY-4.0", "attribution": "   "}, "faixa CC exige a atribuição"),
        ({"title": "♪♪"}, "não gera um id"),
        ({"moods": ()}, "ao menos um clima"),
        ({"moods": (" ",)}, "ao menos um clima"),
        ({"bpm": 0}, "bpm deve ser positivo"),
    ],
)
def test_a_bad_draft_is_refused_before_anything_is_copied(env: Env, over: dict, match: str) -> None:
    with pytest.raises(MusicCatalogError, match=match):
        env.add(**over)
    assert not env.music.exists() or list(env.music.iterdir()) == []


def test_a_cc_track_with_attribution_is_accepted(env: Env) -> None:
    env.add(license_id="CC-BY-4.0", attribution="Alias by Fulano (CC BY 4.0)", artist="Fulano")
    asset = Asset.model_validate_json((env.music / "ytal-alias.json").read_text())
    assert asset.attribution_text.startswith("Alias by Fulano")


def test_unsupported_format_and_missing_file_are_refused(env: Env, tmp_path: Path) -> None:
    bad = tmp_path / "faixa.flac"
    bad.write_bytes(b"x")
    with pytest.raises(MusicCatalogError, match="formato .flac fora de"):
        add_track(env.music, bad, draft(), PROBE, NOW)
    with pytest.raises(MusicCatalogError, match="não existe"):
        add_track(env.music, tmp_path / "nada.mp3", draft(), PROBE, NOW)


def test_the_catalog_is_written_last_and_an_orphan_from_a_failed_attempt_is_replaced(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.pipeline import music_library

    real, written = music_library.write_atomic, []

    def boom(path: Path, data: bytes) -> None:
        written.append(path.name)
        if path.name == "catalog.json":
            raise OSError("disco cheio")
        real(path, data)

    monkeypatch.setattr(music_library, "write_atomic", boom)
    with pytest.raises(OSError, match="disco cheio"):
        env.add()
    assert written == ["ytal-alias.mp3", "ytal-alias.json", "catalog.json"]  # o catálogo por último
    assert load_music_catalog(env.data) is None  # a faixa ainda não existe
    monkeypatch.setattr(music_library, "write_atomic", real)
    env.source.write_bytes(b"audio refeito")
    (env.music / "ytal-alias.ogg").write_bytes(b"sobra de outra extensao")
    env.add()
    assert sorted(p.name for p in env.music.iterdir()) == [
        "catalog.json",
        "ytal-alias.json",
        "ytal-alias.mp3",
    ]
    assert (env.music / "ytal-alias.mp3").read_bytes() == b"audio refeito"


def test_an_invalid_catalog_is_a_catalog_error_naming_the_field(env: Env) -> None:
    env.music.mkdir(parents=True)
    (env.music / "catalog.json").write_text(json.dumps({"tracks": [{"asset_id": "ytal-x"}]}))
    with pytest.raises(MusicCatalogError, match=r"catalog.json: fora do contrato \(tracks.0"):
        env.add()


# --- Instalar no episódio -----------------------------------------------------------------------


def test_installing_copies_the_asset_and_the_media_with_the_asset_last(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env.add()
    seen: list[list[str]] = []
    real = env.store.write
    monkeypatch.setattr(env.store, "write", lambda e, n, m: (seen.append(env.assets()), real(e, n, m))[1])
    assert env.install() is TrackInstallAction.INSTALLED
    assert seen == [["ytal-alias.mp3"]]  # a mídia já estava quando o ativo foi publicado
    assert env.assets() == ["ytal-alias.json", "ytal-alias.mp3"]
    assert env.store.read(EP, "assets/ytal-alias.json", Asset).sha256 == sha256_file(
        env.music / "ytal-alias.mp3"
    )


def test_installing_the_same_track_twice_writes_nothing(env: Env) -> None:
    env.add()
    env.install()
    stamp = (
        env.store.path(EP, "assets/ytal-alias.json").stat().st_mtime_ns,
        env.store.path(EP, "assets/ytal-alias.mp3").stat().st_mtime_ns,
    )
    assert env.install() is TrackInstallAction.UNCHANGED
    assert stamp == (
        env.store.path(EP, "assets/ytal-alias.json").stat().st_mtime_ns,
        env.store.path(EP, "assets/ytal-alias.mp3").stat().st_mtime_ns,
    )


def test_a_catalog_file_that_does_not_match_the_asset_hash_is_refused(env: Env) -> None:
    env.add()
    (env.music / "ytal-alias.mp3").write_bytes(b"alterado a mao depois do registro")
    with pytest.raises(MusicCatalogError, match="não bate com o sha256 do ativo"):
        env.install()
    assert env.assets() == []


def test_an_episode_with_another_version_of_the_track_is_never_overwritten(env: Env) -> None:
    env.add()
    other = Asset.model_validate(
        {
            **Asset.model_validate_json((env.music / "ytal-alias.json").read_text()).model_dump(),
            "sha256": "0" * 64,
        }
    )
    env.store.write(EP, "assets/ytal-alias.json", other)
    with pytest.raises(MusicCatalogError, match="outra versão desta faixa"):
        env.install()
    assert env.store.read(EP, "assets/ytal-alias.json", Asset).sha256 == "0" * 64


def test_a_missing_media_is_restored_unless_the_asset_is_approved(env: Env) -> None:
    env.add()
    env.install()
    env.store.path(EP, "assets/ytal-alias.mp3").unlink()
    assert env.install() is TrackInstallAction.REPAIRED
    assert (env.store.path(EP, "assets/ytal-alias.mp3")).read_bytes() == b"ID3-audio-bytes"
    env.store.path(EP, "assets/ytal-alias.mp3").unlink()
    env.review.record(
        EP,
        ReviewEntry(
            step=Step.ASSETS,
            asset_id="ytal-alias",
            decision=Decision.APPROVED,
            reviewer="Dono",
            at=NOW,
            input_hash="sha256:" + sha256_file(env.music / "ytal-alias.mp3"),
        ),
    )
    # a decisão do gate 3 é sobre o arquivo que sumiu: sem ele, o hash não bate e não há o que proteger
    assert env.install() is TrackInstallAction.REPAIRED


def test_an_approved_asset_with_a_missing_media_is_an_explicit_error(env: Env) -> None:
    env.add()
    env.install()
    approved = Asset.model_validate(
        {**env.store.read(EP, "assets/ytal-alias.json", Asset).model_dump(), "review_status": Status.APPROVED}
    )
    env.store.path(EP, "assets/ytal-alias.json").write_text(approved.model_dump_json(indent=2))
    env.store.path(EP, "assets/ytal-alias.mp3").unlink()
    with pytest.raises(MusicCatalogError, match="vp reopen --step assets --asset ytal-alias"):
        env.install()
    assert env.assets() == ["ytal-alias.json"]  # nada foi recriado


def test_unknown_track_missing_episode_and_a_held_lock_are_errors_without_side_effects(
    env: Env, tmp_path: Path
) -> None:
    env.add()
    with pytest.raises(MusicCatalogError, match="ytal-nada fora do catálogo"):
        env.install("ytal-nada")
    with pytest.raises(MusicCatalogError, match="episódio ep-fantasma não existe"):
        install_track(env.store, env.guard, env.music, "ep-fantasma", "ytal-alias")
    assert not (env.data / "episodes" / "ep-fantasma").exists()
    with env.store.lock(EP), pytest.raises(EpisodeLocked):
        env.install()
    assert env.assets() == []
