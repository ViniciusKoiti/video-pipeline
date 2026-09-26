"""Motor ffmpeg com um episódio sintético minúsculo (320x180, 10 fps): rápido e sem rede."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from app.media.probe import duration_ms, probe_streams
from app.pipeline.schemas import EpisodeManifest, EpisodeScene, VideoSpec
from app.render.ffmpeg import Cue, FfmpegEngine, cues_between, frame_bounds, parse_srt
from tests.fakes import write_silence

SPEC = VideoSpec(width=320, height=180, fps=10)
SRT = (
    "1\n00:00:00,000 --> 00:00:00,900\nThe Proteus sailed.\n\n"
    "2\n00:00:01,000 --> 00:00:01,800\nSix came home.\n"
)


def image(path: Path, color: str, size: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={color}:s={size}", "-frames:v", "1",
         str(path)],
        check=True,
    )


def make_episode(root: Path, gap_ms: int = 0) -> EpisodeManifest:
    image(root / "assets" / "wide.png", "navy", "400x225")
    image(root / "assets" / "tall.png", "darkred", "180x320")
    write_silence(root / "voice" / "S01.wav", 1000)
    write_silence(root / "voice" / "S02.wav", 800)
    (root / "captions.srt").write_text(SRT)
    scenes = [
        EpisodeScene(id="S01", start_ms=0, duration_ms=1000, narration="The Proteus sailed.",
                     asset_id="wide", image="assets/wide.png", audio="voice/S01.wav"),
        EpisodeScene(id="S02", start_ms=1000 + gap_ms, duration_ms=800, narration="Six came home.",
                     asset_id="tall", image="assets/tall.png", audio="voice/S02.wav"),
    ]
    return EpisodeManifest(episode_id="tiny", title="Tiny", language="en", video=SPEC, scenes=scenes,
                           captions="captions.srt")


@pytest.fixture
def engine() -> FfmpegEngine:
    return FfmpegEngine(preset_final="ultrafast", preset_preview="ultrafast")


def test_output_is_h264_aac_16x9_in_limited_range(engine: FfmpegEngine, tmp_path: Path) -> None:
    episode = make_episode(tmp_path / "ep")
    result = engine.render(episode, tmp_path / "ep", tmp_path / "out" / "final.mp4")
    streams = {s["codec_type"]: s for s in probe_streams(result.path)}
    video, audio = streams["video"], streams["audio"]
    assert (video["codec_name"], video["width"], video["height"]) == ("h264", 320, 180)
    assert video["pix_fmt"] == "yuv420p" and video.get("color_range") != "pc"  # nunca faixa cheia (yuvj)
    assert video["r_frame_rate"] == "10/1"
    assert (audio["codec_name"], audio["sample_rate"], audio["channels"]) == ("aac", "48000", 2)
    assert abs(result.duration_ms - 1800) <= 120
    assert (result.width, result.height) == (320, 180)


def test_changing_one_image_rerenders_only_that_scene(engine: FfmpegEngine, tmp_path: Path) -> None:
    episode_dir, out = tmp_path / "ep", tmp_path / "out" / "final.mp4"
    episode = make_episode(episode_dir)
    engine.render(episode, episode_dir, out)
    assert engine.last_run.rendered == ["S01", "S02"]
    engine.render(episode, episode_dir, out)
    assert (engine.last_run.rendered, engine.last_run.reused) == ([], ["S01", "S02"])
    image(episode_dir / "assets" / "tall.png", "darkgreen", "180x320")  # troca a imagem da S02
    engine.render(episode, episode_dir, out)
    assert (engine.last_run.rendered, engine.last_run.reused) == (["S02"], ["S01"])
    assert len(list((out.parent / ".segments-final").glob("S02-*.mp4"))) == 1  # segmento antigo removido


def test_gap_between_scenes_becomes_silence(engine: FfmpegEngine, tmp_path: Path) -> None:
    episode = make_episode(tmp_path / "ep", gap_ms=500)
    result = engine.render(episode, tmp_path / "ep", tmp_path / "out" / "final.mp4")
    assert abs(result.duration_ms - 2300) <= 120


def test_preview_is_720p_and_cached_apart(engine: FfmpegEngine, tmp_path: Path) -> None:
    episode = make_episode(tmp_path / "ep")
    result = engine.render(episode, tmp_path / "ep", tmp_path / "out" / "preview.mp4", preview=True)
    assert (result.width, result.height) == (1280, 720)
    assert (tmp_path / "out" / ".segments-preview").is_dir()
    assert duration_ms(result.path) == result.duration_ms


def test_narrow_images_are_never_cropped(engine: FfmpegEngine) -> None:
    tall = engine.video_filter((1860, 2308), SPEC, 10, None)
    four_by_three = engine.video_filter((2560, 2017), SPEC, 10, None)
    wide = engine.video_filter((2781, 1864), SPEC, 10, None)
    assert "gblur" in tall and "force_original_aspect_ratio=decrease" in tall
    assert "gblur" in four_by_three
    assert "gblur" not in wide and "crop=640:360" in wide


def test_captions_are_burned_only_when_requested(tmp_path: Path) -> None:
    engine = FfmpegEngine()
    assert "subtitles=" in engine.video_filter((1920, 1080), SPEC, 10, tmp_path / "s.srt")
    assert "subtitles=" not in engine.video_filter((1920, 1080), SPEC, 10, None)


def test_frame_bounds_do_not_accumulate_rounding(tmp_path: Path) -> None:
    episode = make_episode(tmp_path)
    thirds = [
        s.model_copy(update={"start_ms": start, "duration_ms": dur})
        for s, (start, dur) in zip(episode.scenes * 2, [(0, 333), (333, 333), (666, 334)], strict=False)
    ]
    thirds = [t.model_copy(update={"id": f"S0{i}"}) for i, t in enumerate(thirds, 1)]
    bounds = frame_bounds(episode.model_copy(update={"scenes": thirds}), fps=30)
    assert bounds == [0, 10, 20, 30]


def test_srt_parsing_and_scene_window() -> None:
    cues = parse_srt(SRT)
    assert cues == [Cue(0, 900, "The Proteus sailed."), Cue(1000, 1800, "Six came home.")]
    assert cues_between(cues, 1000, 1800) == [Cue(0, 800, "Six came home.")]
    assert cues_between(cues, 890, 1800) == [Cue(110, 910, "Six came home.")]  # sobra de 10 ms descartada
    assert cues_between(cues, 800, 1200) == [
        Cue(0, 100, "The Proteus sailed."),
        Cue(200, 400, "Six came home."),
    ]
