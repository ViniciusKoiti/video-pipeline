"""Props do template Remotion (experimento da etapa 8): mesma linha do tempo do motor ffmpeg."""

from pathlib import Path

from app.pipeline.schemas import EpisodeManifest
from app.render.ffmpeg import frame_bounds
from app.render.remotion import RemotionEngine

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"


def episode() -> EpisodeManifest:
    return EpisodeManifest.model_validate_json((FIXTURE / "episode.json").read_text())


def test_props_follow_the_episode_timeline() -> None:
    props = RemotionEngine().props(episode(), FIXTURE, preview=False)
    bounds = frame_bounds(episode(), 30)
    assert (props["width"], props["height"], props["fps"], props["totalFrames"]) == (
        1920,
        1080,
        30,
        bounds[-1],
    )
    assert [s["startFrame"] for s in props["scenes"]] == bounds[:-1]
    assert sum(s["frames"] for s in props["scenes"]) == props["totalFrames"]
    assert props["fadeFrames"] == 9 and not props["burnCaptions"]


def test_narrow_images_are_flagged_by_aspect() -> None:
    scenes = RemotionEngine().props(episode(), FIXTURE, preview=False)["scenes"]
    narrow = [s["id"] for s in scenes if s["aspect"] < 1.45]
    assert narrow == ["S01", "S04", "S05"]  # 4:3 e as duas verticais: inteiras sobre fundo desfocado


def test_preview_is_720p_with_captions_per_scene() -> None:
    props = RemotionEngine().props(episode(), FIXTURE, preview=True)
    assert (props["width"], props["height"]) == (1280, 720) and props["burnCaptions"]
    for scene in props["scenes"]:
        assert all(0 <= c["from"] <= c["to"] <= scene["frames"] for c in scene["cues"])
