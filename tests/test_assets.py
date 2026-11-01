"""RF5 (ativos): busca tolerante a banco indisponível e entrada que preserva cenas e não toca no aprovado."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.bootstrap.archives import available_archives
from app.bootstrap.registry import ConfigurationError, Registration
from app.pipeline.assets import (
    AssetError,
    AssetIntake,
    NoArchiveAvailable,
    media_suffix,
    require_archives,
    search_archives,
)
from app.pipeline.file_hash import sha256_file
from app.pipeline.models.archive_availability import ArchiveAvailability
from app.pipeline.models.intake_action import IntakeAction
from app.pipeline.models.skipped_archive import SkippedArchive
from app.pipeline.ports import EpisodeLocked
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.schemas import Asset, Decision, Provider, ReviewEntry, Status, Step, VisualNeed
from app.providers.archives.base import AssetCandidate, AssetQuery
from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput, PaidApiBlocked, QuotaExhausted
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import make_settings

EP = "ep-ativos"
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
QUERY = AssetQuery(text="cimento", visual_need=VisualNeed.CONTEXTUAL_STOCK)


def make_asset(asset_id: str = "pexels-video-1", **kw: object) -> Asset:
    base = {
        "id": asset_id,
        "provider": Provider.PEXELS,
        "provider_id": "1",
        "original_url": "https://cdn.example.org/v/1.mp4",
        "page_url": "https://example.org/1",
        "author": "Fulano",
        "license_id": "Pexels",
        "attribution_text": "Fulano via Pexels",
        "usage_notes": "conferido",
        "retrieved_at": NOW,
        "review_status": Status.NEEDS_REVIEW,
    }
    return Asset.model_validate({**base, **kw})


class Bank:
    """Um banco de mentira: guarda os downloads e falha onde mandarem."""

    def __init__(
        self, name: str = "pexels", *, found: list[Asset] | None = None, error: Exception | None = None
    ):
        self.info = ProviderInfo(name, remote=False)
        self.found, self.error = found or [], error
        self.downloads: list[str] = []
        self.content, self.fail_download = b"VIDEO-BYTES", None

    def search_assets(self, query: AssetQuery) -> list[AssetCandidate]:
        if self.error:
            raise self.error
        return [AssetCandidate(a) for a in self.found]

    def download_asset(self, asset: Asset, dest: Path) -> Path:
        self.downloads.append(asset.id)
        if self.fail_download:
            raise self.fail_download
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(self.content)
        return dest


# --- Busca --------------------------------------------------------------------------------------


def test_no_available_bank_is_a_diagnosis_not_an_empty_search() -> None:
    skipped = (SkippedArchive("pexels", "PEXELS_API_KEY ausente"), SkippedArchive("coverr", "só manual"))
    with pytest.raises(NoArchiveAvailable, match=r"pexels: PEXELS_API_KEY ausente; coverr: só manual"):
        require_archives(ArchiveAvailability((), skipped))
    bank = Bank()
    assert require_archives(ArchiveAvailability((bank,))) == (bank,)


def test_a_failing_bank_is_recorded_with_its_reason_and_the_others_still_answer() -> None:
    good = Bank("pixabay", found=[make_asset("pixabay-video-9", provider=Provider.PIXABAY)])
    out_of_quota = Bank("pexels", error=QuotaExhausted("pexels", "limite"))
    broken = Bank("unsplash", error=InvalidOutput("unsplash", "JSON inválido"))
    result = search_archives([out_of_quota, good, broken], QUERY)
    assert [(bank, c.asset.id) for bank, c in result.hits] == [("pixabay", "pixabay-video-9")]
    assert [(f.bank, f.reason) for f in result.failures] == [
        ("pexels", "quota_exhausted"),
        ("unsplash", "invalid_output"),
    ]
    assert result.failures[0].query == "cimento" and "limite" in result.failures[0].detail


def test_no_result_is_empty_without_failures_and_differs_from_a_failure() -> None:
    nothing = search_archives([Bank("pexels")], QUERY)
    assert (nothing.hits, nothing.failures) == ([], [])
    failed = search_archives([Bank("pexels", error=QuotaExhausted("pexels", "limite"))], QUERY)
    assert failed.hits == [] and len(failed.failures) == 1


def test_a_blocked_paid_provider_and_programming_errors_stop_the_search() -> None:
    with pytest.raises(PaidApiBlocked):
        search_archives([Bank("a"), Bank("b", error=PaidApiBlocked("b", "pago"))], QUERY)
    with pytest.raises(KeyError):
        search_archives([Bank("a", error=KeyError("bug"))], QUERY)


def test_the_composition_skips_an_unavailable_bank_with_its_reason_and_lets_bugs_through(
    tmp_path: Path,
) -> None:
    settings = make_settings(tmp_path)
    settings = settings.model_copy(
        update={
            "providers": settings.providers.model_copy(
                update={"archives": ["a", "sem-adapter", "sem-chave", "b"]}
            )
        }
    )
    bank_a, bank_b = Bank("a"), Bank("b")

    def no_key(_: object) -> Bank:
        raise ConfigurationError("SEM_CHAVE_API ausente no .env")

    registry = {
        "archives": {
            "a": Registration(1, lambda _: bank_a),
            "sem-chave": Registration(1, no_key),
            "sem-adapter": Registration(1),
            "b": Registration(1, lambda _: bank_b),
        }
    }
    result = available_archives(settings, registry)  # type: ignore[arg-type]
    assert result.archives == (bank_a, bank_b)  # a ordem da cascata
    assert [(s.name, "adapter" in s.reason or "SEM_CHAVE" in s.reason) for s in result.skipped] == [
        ("sem-adapter", True),
        ("sem-chave", True),
    ]

    def bug(_: object) -> Bank:
        raise RuntimeError("erro de programação")

    registry["archives"]["a"] = Registration(1, bug)
    with pytest.raises(RuntimeError, match="programação"):
        available_archives(settings, registry)  # type: ignore[arg-type]


# --- Entrada ------------------------------------------------------------------------------------


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.store = JsonFileStore(tmp_path / "episodes")
        self.review = JsonReviewGate(self.store)
        self.intake = AssetIntake(self.store, ReviewWriteGuard(self.store, self.review))
        self.bank = Bank()

    def take(self, scene: str, asset: Asset | None = None):  # noqa: ANN202
        return self.intake.take(EP, asset or make_asset(), scene, self.bank)

    def asset(self, asset_id: str = "pexels-video-1") -> Asset:
        return self.store.read(EP, f"assets/{asset_id}.json", Asset)

    def media(self, name: str = "pexels-video-1.mp4") -> Path:
        return self.store.path(EP, f"assets/{name}")

    def files(self) -> list[str]:
        folder = self.store.path(EP, "assets")
        return sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


def test_a_new_asset_is_downloaded_with_its_hash_and_scene_and_stays_unapproved(env: Env) -> None:
    result = env.take("S01")
    assert result.action is IntakeAction.DOWNLOADED
    stored = env.asset()
    assert (stored.used_in_scenes, stored.review_status) == (["S01"], Status.NEEDS_REVIEW)
    assert stored.sha256 == sha256_file(env.media()) and env.files() == [
        "pexels-video-1.json",
        "pexels-video-1.mp4",
    ]


def test_choosing_the_same_asset_for_another_scene_keeps_the_first_and_never_downloads_again(
    env: Env,
) -> None:
    env.take("S01")
    again = env.take("S02")
    assert (again.action, env.asset().used_in_scenes, env.bank.downloads) == (
        IntakeAction.SCENE_ADDED,
        ["S01", "S02"],
        ["pexels-video-1"],
    )
    before = env.store.path(EP, "assets/pexels-video-1.json").read_bytes()
    assert env.take("S02").action is IntakeAction.UNCHANGED  # repetir a mesma escolha é idempotente
    assert env.store.path(EP, "assets/pexels-video-1.json").read_bytes() == before
    assert env.bank.downloads == ["pexels-video-1"]


def approve_in_json(env: Env) -> None:
    env.store.write(
        EP, "assets/pexels-video-1.json", env.asset().model_copy(update={"sha256": sha256_file(env.media())})
    )
    approved = Asset.model_validate({**env.asset().model_dump(), "review_status": Status.APPROVED})
    env.store.path(EP, "assets/pexels-video-1.json").write_text(approved.model_dump_json(indent=2))


def test_an_approved_asset_is_never_touched_neither_json_nor_media(env: Env) -> None:
    env.take("S01")
    approve_in_json(env)
    json_bytes, media_bytes = (
        env.store.path(EP, "assets/pexels-video-1.json").read_bytes(),
        env.media().read_bytes(),
    )
    result = env.take("S02")
    assert result.action is IntakeAction.APPROVED_UNTOUCHED
    assert (
        env.store.path(EP, "assets/pexels-video-1.json").read_bytes() == json_bytes
    )  # a cena fica no scenes.json
    assert env.media().read_bytes() == media_bytes and env.bank.downloads == ["pexels-video-1"]


def test_an_approved_asset_with_a_missing_or_different_media_is_an_explicit_error(env: Env) -> None:
    env.take("S01")
    approve_in_json(env)
    env.media().write_bytes(b"outro conteudo")
    with pytest.raises(AssetError, match="vp reopen --step assets --asset pexels-video-1"):
        env.take("S02")
    env.media().unlink()
    with pytest.raises(AssetError, match="aprovado"):
        env.take("S02")
    assert env.bank.downloads == ["pexels-video-1"] and not env.media().exists()  # nada foi recriado


def test_a_gate_three_decision_protects_the_asset_even_when_the_json_status_is_not_approved(env: Env) -> None:
    env.take("S01")
    env.review.record(
        EP,
        ReviewEntry(
            step=Step.ASSETS,
            asset_id="pexels-video-1",
            decision=Decision.APPROVED,
            reviewer="Dono",
            at=NOW,
            input_hash="sha256:" + sha256_file(env.media()),
        ),
    )
    assert env.take("S02").action is IntakeAction.APPROVED_UNTOUCHED
    assert env.asset().used_in_scenes == ["S01"]


def test_an_unapproved_asset_with_a_changed_media_is_downloaded_again_keeping_its_scenes(env: Env) -> None:
    env.take("S01")
    env.media().write_bytes(b"corrompido")
    result = env.take("S02")
    assert result.action is IntakeAction.REPAIRED and env.bank.downloads == ["pexels-video-1"] * 2
    assert (env.asset().used_in_scenes, env.asset().sha256) == (["S01", "S02"], sha256_file(env.media()))
    assert env.media().read_bytes() == b"VIDEO-BYTES"


def test_a_failed_download_leaves_no_file_and_an_empty_one_is_refused(env: Env) -> None:
    env.bank.fail_download = QuotaExhausted("pexels", "cota")
    with pytest.raises(QuotaExhausted):
        env.take("S01")
    assert env.files() == []
    env.bank.fail_download, env.bank.content = None, b""
    with pytest.raises(AssetError, match="vazio"):
        env.take("S01")
    assert env.files() == []  # nem a mídia vazia nem o temporário ficam


def test_a_failure_before_the_json_leaves_an_orphan_media_that_the_retry_replaces(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = env.store.write

    def boom(episode_id: str, name: str, manifest: object) -> None:
        raise OSError("disco cheio")

    monkeypatch.setattr(env.store, "write", boom)
    with pytest.raises(OSError, match="disco cheio"):
        env.take("S01")
    assert env.files() == ["pexels-video-1.mp4"]  # mídia sem JSON: o ativo ainda não existe
    monkeypatch.setattr(env.store, "write", real)
    assert env.take("S01").action is IntakeAction.DOWNLOADED and env.asset().used_in_scenes == ["S01"]
    assert env.files() == ["pexels-video-1.json", "pexels-video-1.mp4"]


def test_the_json_is_published_after_the_media(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[list[str]] = []
    real = env.store.write
    monkeypatch.setattr(env.store, "write", lambda e, n, m: (seen.append(env.files()), real(e, n, m))[1])
    env.take("S01")
    assert seen == [["pexels-video-1.mp4"]]


def test_the_episode_lock_is_exclusive_for_the_intake(env: Env) -> None:
    with env.store.lock(EP), pytest.raises(EpisodeLocked):
        env.take("S01")
    assert env.bank.downloads == []


@pytest.mark.parametrize(
    ("asset_id", "url", "expected"),
    [
        ("pexels-video-1", "https://cdn.example.org/a/clip.WEBM?x=1", ".webm"),
        ("pexels-video-1", "https://cdn.example.org/a/clip", ".mp4"),
        ("pexels-photo-1", "https://cdn.example.org/a/foto", ".jpg"),
        ("pexels-photo-1", None, ".jpg"),
        ("pexels-photo-1", "https://cdn.example.org/a/foto.png", ".png"),
    ],
)
def test_the_media_suffix_comes_from_the_url_then_from_the_kind_of_asset(
    asset_id: str, url: str | None, expected: str
) -> None:
    assert media_suffix(make_asset(asset_id, original_url=url)) == expected
