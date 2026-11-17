"""Relógio de retenção do vídeo longo (ADR 061): promessa até 0:30, gancho ou virada entre 2:00 e 3:00, gancho
logo depois da pausa de aviso, com o tempo da voz real quando ela existe."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.pipeline.retention_clock import (
    mmss,
    pause_hints,
    retention_attention,
    retention_summary,
    scene_clock,
)
from app.pipeline.schemas import ScenesManifest
from app.pipeline.voice_timeline import measured_seconds
from app.storage.json_files import JsonFileStore

EP = "ep"


def manifest(*scenes: tuple[str, str | None]) -> ScenesManifest:
    """Uma cena por (fala, beat), com ids S01, S02..."""
    raw: list[dict[str, Any]] = []
    for i, (text, beat) in enumerate(scenes, start=1):
        scene: dict[str, Any] = {"id": f"S{i:02d}", "narration": text, "visual_need": "contextual_stock",
                                 "search_query": "x"}
        if beat:
            scene["beat"] = beat
        raw.append(scene)
    return ScenesManifest.model_validate({"episode_id": EP, "language": "pt-BR", "scenes": raw})


def timed(beats: list[str | None], seconds: list[float]) -> tuple[list[Any], str]:
    scenes = manifest(*[("Uma fala.", beat) for beat in beats])
    measured = {scene.id: length for scene, length in zip(scenes.scenes, seconds, strict=True)}
    return scene_clock(scenes, 15.0, measured)


GOOD = (["promise", None, "rehook", None, "pause", "rehook", None], [25, 100, 20, 30, 15, 15, 100])


def test_a_long_video_with_the_beats_in_place_passes() -> None:
    clock, source = timed(*GOOD)
    assert source == "voz real"
    assert retention_attention(clock, source) == []
    assert retention_summary(clock, source) == (
        "relógio (voz real): 5:05; S01 promise 0:00, S03 rehook 2:05, S05 pause 2:55, S06 rehook 3:10"
    )


def test_shorts_are_left_alone() -> None:
    clock, source = timed([None, None], [30, 20])
    assert retention_attention(clock, source) == [] and retention_summary(clock, source) is None


def test_a_long_script_without_beats_asks_for_them() -> None:
    clock, source = timed([None, None], [200, 100])
    (line,) = retention_attention(clock, source)
    assert "sem `beat`" in line and "ADR 061" in line


def test_a_late_promise() -> None:
    beats, seconds = GOOD
    clock, source = timed(beats, [34, *seconds[1:]])
    (line,) = retention_attention(clock, source)
    assert line == "relógio (voz real): a promessa fecha em ~0:34 (S01); o alvo é até 0:30"


def test_no_rehook_between_two_and_three_minutes() -> None:
    """O `vazio-de-ter-tudo`: a prévia em ~1:02 e a virada só em ~5:24."""
    clock, source = timed(["promise", "rehook", None, "turn", None], [25, 20, 280, 15, 30])
    (line,) = retention_attention(clock, source)
    assert "entre 2:00 e 3:00; o próximo é S04, em ~5:25" in line


def test_a_rehook_that_starts_before_two_minutes_and_runs_into_the_window_counts() -> None:
    clock, source = timed(["promise", None, "turn", None], [25, 90, 10, 200])
    assert retention_attention(clock, source) == []  # 1:55 a 2:05


def test_after_a_warning_pause_comes_a_rehook() -> None:
    beats = ["promise", None, "rehook", "pause", "pause", None, None]
    clock, source = timed(beats, [25, 100, 20, 10, 10, 20, 100])
    (line,) = retention_attention(clock, source)
    assert line.startswith("relógio (voz real): depois da pausa em S05 (~2:45), S06 não é gancho")


def test_a_warning_scene_without_the_pause_beat_is_pointed_out() -> None:
    scenes = manifest(("Fala longa. " * 300, None), ("O CVV atende pelo <short pause> 188.", None))
    clock, _ = scene_clock(scenes, 15.0)
    (hint,) = pause_hints(clock)
    assert hint.startswith("S02: fala de aviso (CVV) sem `beat: pause`")
    marked = manifest(("Fala longa. " * 300, None), ("O Centro de Valorização da Vida atende.", "pause"))
    assert pause_hints(scene_clock(marked, 15.0)[0]) == []


def test_the_estimate_comes_from_the_text() -> None:
    clock, source = scene_clock(manifest(("a" * 150, None), ("b" * 300, None)), 15.0)
    assert source == "estimado"
    assert [(start, end) for _, start, end in clock] == [(0.0, 10.0), (10.0, 30.0)]
    assert mmss(125.4) == "2:05" and mmss(59.6) == "1:00"


def test_measured_seconds_come_from_the_voice_in_the_manifest(tmp_path: Path) -> None:
    store = JsonFileStore(tmp_path / "episodes")
    folder = store.path(EP, "")
    (folder / "voice").mkdir(parents=True)
    for name in ("S01.wav", "S02.wav"):
        (folder / "voice" / name).write_bytes(b"x")
    scenes = {sid: {"status": "completed", "outputs": [f"voice/{sid}.wav"]} for sid in ("S01", "S02")}
    manifest_file = {"episode_id": EP, "steps": {"voice": {"status": "completed", "scenes": scenes}}}
    (folder / "manifest.json").write_text(json.dumps(manifest_file), encoding="utf-8")
    lengths = {"S01.wav": 3.5, "S02.wav": 4.0}
    assert measured_seconds(store, EP, ["S01", "S02"], lambda p: lengths[p.name]) == {"S01": 3.5, "S02": 4.0}
    assert measured_seconds(store, EP, ["S01", "S02", "S03"], lambda p: 1.0) is None  # cena sem voz: estima
    (folder / "voice" / "S02.wav").unlink()
    assert measured_seconds(store, EP, ["S01", "S02"], lambda p: 1.0) is None  # WAV sumiu: estima
