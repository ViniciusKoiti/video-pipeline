"""Props das cenas do template Remotion (formato explainer, ADR 008): sem renderizar, sem Node."""

from __future__ import annotations

from pathlib import Path

from app.pipeline.schemas import EpisodeManifest
from app.render.ffmpeg import frame_bounds
from app.render.remotion import PROJECT, RemotionEngine, template_hash
from tests.test_shots import v2_episode

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"


def test_v1_episode_becomes_one_photo_shot_per_scene() -> None:
    episode = EpisodeManifest.model_validate_json((FIXTURE / "episode.json").read_text())
    props = RemotionEngine().scene_props(episode, FIXTURE, preview=False)
    bounds = frame_bounds(episode, 30)
    assert [p["frames"] for p in props] == [b - a for a, b in zip(bounds, bounds[1:], strict=False)]
    for scene_props, scene in zip(props, episode.scenes, strict=True):
        (shot,) = scene_props["shots"]
        assert (shot["from"], shot["frames"], shot["spec"]["kind"], shot["media"]) == (
            0,
            scene_props["frames"],
            "photo",
            scene.image,
        )
        assert shot["aspect"] > 0
    assert props[0]["shots"][0]["credit"].startswith("George W. Rice")  # attribution_text do ativo
    assert props[0]["cues"] == []  # final sem legendas


def test_v2_shots_are_contiguous_in_frames(tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "f.jpg").write_bytes(
        (FIXTURE / "assets" / "commons-lc-usz62-136192.jpg").read_bytes()
    )
    episode = EpisodeManifest.model_validate(v2_episode())
    (scene,) = RemotionEngine().scene_props(episode, tmp_path, preview=True)
    starts = [s["from"] for s in scene["shots"]]
    assert starts[0] == 0 and starts == sorted(starts)
    assert sum(s["frames"] for s in scene["shots"]) == scene["frames"]
    assert [s["media"] for s in scene["shots"]] == [None, None, "assets/f.jpg", None]
    assert (scene["width"], scene["height"]) == (1280, 720)


def test_preview_carries_captions_per_scene() -> None:
    episode = EpisodeManifest.model_validate_json((FIXTURE / "episode.json").read_text())
    props = RemotionEngine().scene_props(episode, FIXTURE, preview=True)
    assert any(p["cues"] for p in props)
    for p in props:
        assert all(0 <= c["from"] <= c["to"] <= p["frames"] for c in p["cues"])


def test_template_hash_covers_sources_and_fonts() -> None:
    assert len(template_hash(PROJECT)) == 64
    assert any(PROJECT.glob("src/fonts/*.woff2"))
