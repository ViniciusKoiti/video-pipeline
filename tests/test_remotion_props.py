"""Props das cenas do template Remotion (formato explainer, ADR 008): sem renderizar, sem Node."""

from __future__ import annotations

import subprocess
from pathlib import Path

from app.pipeline.schemas import EpisodeManifest
from app.render.ffmpeg import frame_bounds
from app.render.remotion import PROJECT, RemotionEngine, footage_continuity, template_hash
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


def test_portrait_scene_with_recognized_words_carries_them(tmp_path: Path) -> None:
    from app.media.word_captions import WORDS, SceneSpeech, sync_words
    from app.pipeline.schemas import VideoSpec
    from app.providers.alignment.base import TimedWord

    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "f.jpg").write_bytes(
        (FIXTURE / "assets" / "commons-lc-usz62-136192.jpg").read_bytes()
    )
    episode = EpisodeManifest.model_validate(v2_episode())
    (scene,) = episode.scenes
    speech = [SceneSpeech(scene.id, scene.audio, scene.narration, scene.duration_ms)]
    sync_words(tmp_path / WORDS, speech, lambda s: [TimedWord("x", 0, 500)], "fake")
    (landscape,) = RemotionEngine().scene_props(episode, tmp_path, preview=True)
    assert "words" not in landscape  # paisagem: só a legenda por frase
    portrait = episode.model_copy(update={"video": VideoSpec.for_orientation("portrait")})
    (props,) = RemotionEngine().scene_props(portrait, tmp_path, preview=True)
    assert props["words"] and props["words"][0]["from"] == 0
    assert all(0 <= w["from"] <= w["to"] <= props["frames"] for w in props["words"])


def _media(kind: str, start: int, media: str | None = "assets/a.mp4") -> dict[str, object]:
    return {"from": start, "spec": {"kind": kind}, "media": media if kind in ("photo", "broll") else None}


def _scene(frames: int, *shots: dict[str, object]) -> dict[str, object]:
    return {"frames": frames, "shots": list(shots)}


def test_same_broll_continues_across_scenes_without_fade() -> None:
    props = [_scene(90, _media("broll", 0)), _scene(60, _media("broll", 0))]
    footage_continuity(props, lambda media: 300)
    assert "startFrom" not in props[0]["shots"][0] and props[1]["shots"][0]["startFrom"] == 90
    assert props[0]["fadeOut"] is False and props[1]["fadeIn"] is False
    assert all("loopFrames" not in s for p in props for s in p["shots"])


def test_broll_longer_than_the_clip_loops_and_keeps_the_phase() -> None:
    props = [_scene(400, _media("broll", 0)), _scene(100, _media("broll", 0))]
    footage_continuity(props, lambda media: 300)
    assert props[0]["shots"][0] == {**_media("broll", 0), "loopFrames": 300}
    assert (props[1]["shots"][0]["startFrom"], props[1]["shots"][0]["loopFrames"]) == (100, 300)


def test_continuity_breaks_on_another_media_but_not_on_overlays() -> None:
    props = [
        _scene(90, _media("broll", 0), _media("keyword", 30), _media("photo", 60, "assets/f.jpg")),
        _scene(60, _media("broll", 0)),
        _scene(60, _media("keyword", 0), _media("broll", 20)),
    ]
    footage_continuity(props, lambda media: 300)
    assert "startFrom" not in props[1]["shots"][0] and "fadeOut" not in props[0]  # a foto cortou a textura
    # a cena 3 abre com um gráfico: o vídeo segue a fase (60 quadros tocados), mas a cena mantém o fade
    assert props[2]["shots"][1]["startFrom"] == 60 and "fadeIn" not in props[2] and "fadeOut" not in props[1]


def test_scene_props_loop_a_clip_shorter_than_the_shot(tmp_path: Path) -> None:
    (tmp_path / "assets").mkdir()
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=64x36:rate=30:duration=2",
         str(tmp_path / "assets" / "f.mp4")],
        check=True,
    )
    raw = v2_episode()
    for shot in raw["scenes"][0]["shots"]:
        if shot["spec"]["kind"] == "photo":
            spec = {k: v for k, v in shot["spec"].items() if k not in ("crop", "motion")}
            shot.update(media="assets/f.mp4", spec={**spec, "kind": "broll"})
    episode = EpisodeManifest.model_validate(raw)
    (scene,) = RemotionEngine().scene_props(episode, tmp_path, preview=True)
    (broll,) = [s for s in scene["shots"] if s["spec"]["kind"] == "broll"]
    assert broll["frames"] > 2 * scene["fps"]  # o plano vai até o fim da cena, mais longo que o clipe de 2 s
    assert broll["loopFrames"] == 2 * scene["fps"] and "startFrom" not in broll
