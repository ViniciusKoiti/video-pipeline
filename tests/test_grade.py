"""Grade de cor do B-roll (ADR 057): `tratamento.json` põe ativos de clipe em preto e branco."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from app.pipeline.schemas import EpisodeManifest
from app.render.grade import GradeInvalid, mono_assets
from app.render.remotion import RemotionEngine
from tests.test_shots import v2_episode


def _write(tmp_path: Path, content: object) -> None:
    (tmp_path / "tratamento.json").write_text(json.dumps(content))


def test_no_file_means_no_mono_assets(tmp_path: Path) -> None:
    assert mono_assets(tmp_path) == frozenset()


def test_mono_assets_reads_the_ids(tmp_path: Path) -> None:
    _write(tmp_path, {"mono": ["a", "b"]})
    assert mono_assets(tmp_path) == frozenset({"a", "b"})


BAD = [["a"], {"mono": "a"}, {"mono": [1]}, {"mono": [""]}, {"mono": [], "x": 1}]


@pytest.mark.parametrize("content", BAD)
def test_malformed_file_is_an_error(tmp_path: Path, content: object) -> None:
    _write(tmp_path, content)
    with pytest.raises(GradeInvalid):
        mono_assets(tmp_path)


def test_invalid_json_is_an_error(tmp_path: Path) -> None:
    (tmp_path / "tratamento.json").write_text("{")
    with pytest.raises(GradeInvalid):
        mono_assets(tmp_path)


def _scene_props(tmp_path: Path, asset_id: str) -> list[dict]:
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
            shot.update(media="assets/f.mp4", spec={**spec, "kind": "broll", "asset_id": asset_id})
    episode = EpisodeManifest.model_validate(raw)
    (scene,) = RemotionEngine().scene_props(episode, tmp_path, preview=True)
    return [s for s in scene["shots"] if s["spec"]["kind"] == "broll"]


def test_listed_clip_gets_the_mono_grade(tmp_path: Path) -> None:
    _write(tmp_path, {"mono": ["clip-a"]})
    (broll,) = _scene_props(tmp_path, "clip-a")
    assert broll["grade"] == "mono"


def test_unlisted_clip_keeps_its_props_unchanged(tmp_path: Path) -> None:
    _write(tmp_path, {"mono": ["clip-a"]})
    (broll,) = _scene_props(tmp_path, "clip-b")
    assert "grade" not in broll
