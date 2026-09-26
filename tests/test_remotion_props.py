"""Props por cena do template Remotion + motion-kit (experimento da etapa 8)."""

from pathlib import Path

from app.pipeline.schemas import EpisodeManifest
from app.render.ffmpeg import frame_bounds
from app.render.remotion import PROJECT, RemotionEngine, template_hash

FIXTURE = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"


def episode() -> EpisodeManifest:
    return EpisodeManifest.model_validate_json((FIXTURE / "episode.json").read_text())


def test_one_composition_per_scene_following_the_timeline() -> None:
    props = RemotionEngine().scene_props(episode(), FIXTURE, preview=False)
    bounds = frame_bounds(episode(), 30)
    assert [p["frames"] for p in props] == [b - a for a, b in zip(bounds, bounds[1:], strict=False)]
    assert all((p["width"], p["height"], p["fps"]) == (1920, 1080, 30) for p in props)
    assert all(p["fadeFrames"] == 9 and p["cues"] == [] for p in props)  # final sem legendas


def test_narrow_images_are_flagged_by_aspect() -> None:
    props = RemotionEngine().scene_props(episode(), FIXTURE, preview=False)
    assert [p["image"].split("/")[-1][:18] for p in props if p["aspect"] < 1.45] == [
        "commons-rice-prote",
        "commons-111-sc-911",
        "commons-111-sc-962",
    ]


def test_look_varies_per_scene_and_scales_with_resolution() -> None:
    final = RemotionEngine().scene_props(episode(), FIXTURE, preview=False)
    preview = RemotionEngine().scene_props(episode(), FIXTURE, preview=True)
    assert len({p["look"]["phase"] for p in final}) == len(final)  # deriva dessincronizada
    assert (final[0]["look"]["driftX"], preview[0]["look"]["driftX"]) == (22, 15)
    assert any(p["cues"] for p in preview) and (preview[0]["width"], preview[0]["height"]) == (1280, 720)
    for p in preview:
        assert all(0 <= c["from"] <= c["to"] <= p["frames"] for c in p["cues"])


def test_template_hash_covers_the_template_sources() -> None:
    assert len(template_hash(PROJECT)) == 64
