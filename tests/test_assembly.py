"""RF6 (render): o motor vem da porta, a montagem incompleta não o alcança, prévia e final não se misturam."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.bootstrap.registry import ConfigurationError
from app.pipeline.assembly import AssemblyError, EpisodeRenderer, assembly_problems, asset_ids
from app.pipeline.gates import record_decision
from app.pipeline.ports import EpisodeLocked, ImmutableManifest
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.reopen import reopen_gate
from app.pipeline.schemas import (
    Asset,
    Decision,
    EpisodeFormat,
    EpisodeManifest,
    ScenesManifest,
    Status,
    Step,
    VideoSpec,
)
from app.storage.json_files import JsonFileStore, JsonReviewGate
from tests.fakes import FakeRender, write_silence
from tests.test_gates import stock_asset

EP = "ep-montagem"
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


def scenes_manifest() -> ScenesManifest:
    raw = {
        "episode_id": EP,
        "language": "pt-BR",
        "scenes": [
            {
                "id": "S01",
                "narration": "Primeira cena.",
                "visual_need": "contextual_stock",
                "search_query": "a",
                "chosen_asset_id": "pexels-video-1",
            },
            {
                "id": "S02",
                "narration": "Segunda cena.",
                "visual_need": "contextual_stock",
                "search_query": "b",
                "chosen_asset_id": "pexels-video-2",
            },
        ],
    }
    return ScenesManifest.model_validate(raw)


def episode_manifest(*, music: list[dict] | None = None, title: str = "Montagem") -> EpisodeManifest:
    scenes = [
        {
            "id": f"S0{i}",
            "start_ms": (i - 1) * 1000,
            "duration_ms": 1000,
            "narration": "Fala.",
            "audio": f"voice/S0{i}.wav",
            "shots": [
                {
                    "start_ms": 0,
                    "duration_ms": 1000,
                    "spec": {"kind": "keyword", "text": "x", "anchor": "Fala"},
                }
            ],
        }
        for i in (1, 2)
    ]
    return EpisodeManifest.model_validate(
        {
            "schema_version": 2,
            "episode_id": EP,
            "title": title,
            "language": "pt-BR",
            "format": EpisodeFormat.EXPLAINER,
            "scenes": scenes,
            "video": VideoSpec.for_orientation("landscape"),
            "music": music or [],
        }
    )


class Spy(FakeRender):
    def __init__(self, name: str = "fake-render") -> None:
        super().__init__(name)
        self.calls: list[tuple[str, bool]] = []

    def render(self, episode, episode_dir, out, *, preview=False):  # type: ignore[no-untyped-def]
        self.calls.append((out.name, preview))
        return super().render(episode, episode_dir, out, preview=preview)


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.store = JsonFileStore(tmp_path / "episodes")
        self.review = JsonReviewGate(self.store)
        self.guard = ReviewWriteGuard(self.store, self.review)
        self.engine = Spy()
        self.asked: list[EpisodeFormat] = []
        self.renderer = EpisodeRenderer(self.store, self.guard, self._engine_for)
        self.scenes, self.episode = scenes_manifest(), episode_manifest()
        folder = self.store.path(EP, "")
        (folder / "assets").mkdir(parents=True)
        (folder / "voice").mkdir()
        for scene in ("S01", "S02"):
            write_silence(folder / "voice" / f"{scene}.wav", 1000)
        for asset_id in ("pexels-video-1", "pexels-video-2"):
            stock_asset(folder, asset_id)

    def _engine_for(self, episode_format: EpisodeFormat) -> Spy:
        self.asked.append(episode_format)
        return self.engine

    def path(self, name: str) -> Path:
        return self.store.path(EP, name)

    def approve_assets(self) -> None:
        for asset_id in ("pexels-video-1", "pexels-video-2"):
            asset = self.store.read(EP, f"assets/{asset_id}.json", Asset)
            approved = Asset.model_validate({**asset.model_dump(), "review_status": Status.APPROVED})
            self.path(f"assets/{asset_id}.json").write_text(approved.model_dump_json(indent=2))

    def approve_gate4(self) -> None:
        record_decision(
            self.store, self.review, EP, Step.PREVIEW, Decision.APPROVED, reviewer="Dono", now=lambda: NOW
        )

    def render(self, *, preview: bool):  # type: ignore[no-untyped-def]
        return self.renderer.render(EP, self.scenes, self.episode, preview=preview)


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


# --- O motor vem da porta -------------------------------------------------------------------------


def test_the_engine_comes_from_the_port_by_the_episode_format_and_can_be_swapped(env: Env) -> None:
    result = env.render(preview=True)
    assert env.asked == [EpisodeFormat.EXPLAINER] and env.engine.calls == [("preview.mp4", True)]
    assert result.path == env.path("renders/preview.mp4") and result.path.stat().st_size > 0
    other = Spy("outro-motor")  # trocar o motor é só a composição entregar outro
    env.engine = other
    env.render(preview=True)
    assert other.calls == [("preview.mp4", True)] and other.info.name == "outro-motor"


def test_a_format_without_an_engine_is_a_configuration_error_and_nothing_is_written(env: Env) -> None:
    def none(_: EpisodeFormat) -> Spy:
        raise ConfigurationError("nenhum motor de render para o formato explainer")

    renderer = EpisodeRenderer(env.store, env.guard, none)
    with pytest.raises(ConfigurationError, match="nenhum motor"):
        renderer.render(EP, env.scenes, env.episode, preview=True)
    assert not env.path("episode.json").exists() and not env.path("renders").exists()


# --- Montagem incompleta --------------------------------------------------------------------------


def test_the_used_assets_are_the_ones_of_the_shots_and_of_the_music() -> None:
    music = [
        {
            "asset_id": "ytal-alias",
            "media": "assets/ytal-alias.mp3",
            "role": "bed",
            "start_ms": 0,
            "end_ms": 2000,
            "gain_db": -20.0,
        }
    ]
    assert asset_ids(scenes_manifest(), episode_manifest(music=music)) == [
        "pexels-video-1",
        "pexels-video-2",
        "ytal-alias",
    ]


def test_an_incomplete_assembly_never_reaches_the_engine(env: Env) -> None:
    env.path("voice/S02.wav").unlink()
    env.path("voice/S01.wav").write_bytes(b"nao e um wav")
    env.path("assets/pexels-video-2.mp4").unlink()
    with pytest.raises(AssemblyError, match=r"montagem incompleta \(3\)") as raised:
        env.render(preview=True)
    message = str(raised.value)
    assert "S01: falta o WAV voice/S01.wav" in message and "S02: falta o WAV voice/S02.wav" in message
    assert "ativo pexels-video-2: sem arquivo de mídia em assets/" in message
    assert env.engine.calls == [] and not env.path("episode.json").exists()  # nem o episode.json foi escrito


def test_the_preview_is_a_draft_but_the_final_needs_the_assets_approved(env: Env) -> None:
    env.render(preview=True)  # ativos ainda em needs_review: a prévia sai
    with pytest.raises(AssemblyError, match=r"render final incompleto \(2\)") as raised:
        env.render(preview=False)
    assert "ativo pexels-video-1: não aprovado no gate 3" in str(raised.value)
    assert env.engine.calls == [("preview.mp4", True)] and not env.path("renders/final.mp4").exists()
    env.approve_assets()
    assert env.render(preview=False).path == env.path("renders/final.mp4")
    assert env.engine.calls[-1] == ("final.mp4", False)


def test_a_music_asset_must_also_be_approved_for_the_final(env: Env) -> None:
    env.approve_assets()
    music = [
        {
            "asset_id": "ytal-alias",
            "media": "assets/ytal-alias.mp3",
            "role": "bed",
            "start_ms": 0,
            "end_ms": 2000,
            "gain_db": -20.0,
        }
    ]
    env.episode = episode_manifest(music=music)
    env.path("assets/ytal-alias.mp3").write_bytes(b"ID3")
    problems = assembly_problems(env.store, EP, env.scenes, env.episode, final=True)
    assert problems == [
        "ativo ytal-alias: não aprovado no gate 3 (o render final exige)"
    ]  # sem o JSON do ativo
    assert assembly_problems(env.store, EP, env.scenes, env.episode, final=False) == []


# --- Prévia e final, e o gate 4 -------------------------------------------------------------------


def test_preview_and_final_are_different_files_and_each_render_leaves_the_other_alone(env: Env) -> None:
    env.approve_assets()
    env.render(preview=True)
    before = env.path("renders/preview.mp4").read_bytes()
    env.render(preview=False)
    assert sorted(p.name for p in env.path("renders").iterdir()) == ["final.mp4", "preview.mp4"]
    assert env.path("renders/preview.mp4").read_bytes() == before


def test_an_approved_preview_refuses_a_render_over_it_before_the_engine_runs(env: Env) -> None:
    env.render(preview=True)
    env.approve_gate4()
    calls = list(env.engine.calls)
    with pytest.raises(ImmutableManifest, match="renders/preview.mp4 está carimbado pelo gate de preview"):
        env.render(preview=True)
    assert env.engine.calls == calls
    reopen_gate(
        env.store, env.review, EP, Step.PREVIEW, reviewer="Dono", reason="refazer a prévia", now=lambda: NOW
    )
    env.render(preview=True)
    assert env.engine.calls == [*calls, ("preview.mp4", True)]


def test_the_final_is_allowed_after_an_approved_preview_and_then_the_final_is_protected(env: Env) -> None:
    env.approve_assets()
    env.render(preview=True)
    env.approve_gate4()  # carimba a prévia (ainda não há final)
    env.render(
        preview=False
    )  # o final é outro arquivo: permitido, e a aprovação passa a pedir nova decisão (#120)
    env.approve_gate4()  # agora carimba o final
    with pytest.raises(ImmutableManifest, match="renders/final.mp4"):
        env.render(preview=False)


def test_an_approved_episode_json_is_not_changed_and_the_same_one_is_not_a_problem(env: Env) -> None:
    env.render(preview=True)
    env.approve_gate4()
    stamp = env.path("episode.json").stat().st_mtime_ns
    assert env.renderer.assemble(EP, env.scenes, env.episode) is False  # o mesmo: nada escrito
    assert env.path("episode.json").stat().st_mtime_ns == stamp
    env.episode = episode_manifest(title="Outro título")
    with pytest.raises(ImmutableManifest, match="episode.json está carimbado"):
        env.renderer.assemble(EP, env.scenes, env.episode)
    assert "Montagem" in env.path("episode.json").read_text()


# --- Gravação, lock e o modo sem render -----------------------------------------------------------


def test_episode_json_is_written_whole_and_a_failure_keeps_the_old_one_and_skips_the_engine(
    env: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.pipeline import assembly

    env.render(preview=True)
    old = env.path("episode.json").read_bytes()
    env.episode = episode_manifest(title="Novo título")
    real = assembly.write_atomic

    def boom(path: Path, data: bytes) -> None:
        raise OSError("disco cheio")

    monkeypatch.setattr(assembly, "write_atomic", boom)
    calls = list(env.engine.calls)
    with pytest.raises(OSError, match="disco cheio"):
        env.render(preview=True)
    assert env.path("episode.json").read_bytes() == old and env.engine.calls == calls
    monkeypatch.setattr(assembly, "write_atomic", real)
    env.render(preview=True)
    assert "Novo título" in env.path("episode.json").read_text()


def test_assemble_writes_the_episode_without_rendering_and_checks_the_draft_level(env: Env) -> None:
    assert env.renderer.assemble(EP, env.scenes, env.episode) is True
    assert env.engine.calls == [] and env.path("episode.json").is_file() and env.asked == []
    env.path("voice/S01.wav").unlink()
    with pytest.raises(AssemblyError, match=r"montagem incompleta \(1\)"):
        env.renderer.assemble(EP, env.scenes, env.episode)


def test_the_episode_lock_is_exclusive_for_the_render(env: Env) -> None:
    with env.store.lock(EP), pytest.raises(EpisodeLocked):
        env.render(preview=True)
    assert env.engine.calls == [] and not env.path("episode.json").exists()


def test_episode_json_has_the_same_bytes_the_script_wrote_before(env: Env) -> None:
    """O script gravava `episode.model_dump_json(indent=2)` sem quebra de linha no fim: o arquivo não muda."""
    env.render(preview=True)
    assert env.path("episode.json").read_bytes() == env.episode.model_dump_json(indent=2).encode("utf-8")
    assert not env.path("episode.json").read_bytes().endswith(b"\n")
