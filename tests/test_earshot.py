"""Conferência de áudio com o earshot (ADR 035, emenda): o JSON dele é lido e o que foge do alvo é listado."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.media import earshot
from app.media.earshot import AudioReview, CueSync, parse_review, review_problems, run_timeline


def timeline_json(lufs: float = -14.0, items: list[dict] | None = None, pulse: float = 0.06) -> dict:
    """Um JSON do `earshot timeline` com só o que o parser lê, nas chaves reais."""
    return {
        "duration": 38.2,
        "loudness": {"integrated_lufs": lufs, "true_peak_dbtp": -1.5, "lra_lu": 4.5},
        "music": {"tempo": 74.7, "pulse_clarity": pulse, "beats": [0.03, 0.96]},
        "sync": {
            "cuts": {"items": [], "stats": {}},
            "cues": {
                "items": items
                if items is not None
                else [
                    {"t": 5.2, "kind": "cue", "offset_ms": 26.0, "status": "OK", "event": "chat message pop"},
                    {"t": 15.6, "kind": "cue", "offset_ms": -9.0, "status": "OK", "event": "short swish"},
                ],
                "stats": {"n": 2, "median_abs_offset_ms": 20.0, "chance_within_40ms": 0.366},
            },
        },
    }


def test_parse_reads_loudness_beat_and_cues() -> None:
    review = parse_review(timeline_json())
    assert review.integrated_lufs == -14.0 and review.true_peak_dbtp == -1.5
    assert review.tempo_bpm == 74.7 and not review.has_beat  # pulso 0,06 < 0,15: sem grade de batidas
    assert [c.at_s for c in review.cues] == [5.2, 15.6] and all(c.hit for c in review.cues)
    assert review.median_abs_offset_ms == 20.0 and review.chance_within_tolerance == 0.366
    assert parse_review(timeline_json(pulse=0.4)).has_beat


def test_mono_short_measured_like_youtube_is_out_of_target() -> None:
    # O caso medido em 2026-10-31: o ffmpeg diz −15 num Short mono; nos dois alto-falantes são −12.
    problems = review_problems(parse_review(timeline_json(lufs=-12.0)))
    assert len(problems) == 1 and problems[0].startswith("volume efetivo (mono nos dois alto-falantes")
    assert review_problems(parse_review(timeline_json(lufs=-14.0))) == []


def test_cut_with_a_planned_effect_and_no_hit_is_a_problem() -> None:
    items = [
        {"t": 5.2, "kind": "cue", "offset_ms": 120.0, "status": "near", "event": None},
        {"t": 15.6, "kind": "cue", "offset_ms": None, "status": "no hit", "event": None},
        {"t": 24.6, "kind": "cue", "offset_ms": None, "status": "no hit", "event": None},
    ]
    review = parse_review(timeline_json(items=items))
    problems = review_problems(review, expected_hits={5.2, 15.6})
    assert problems == [
        "corte em 5.20 s tinha efeito no plano e ficou ataque a +120 ms",
        "corte em 15.60 s tinha efeito no plano e ficou sem som",
    ]  # 24,6 s não tinha efeito no plano: só informação


def test_true_peak_above_the_ceiling_is_a_problem() -> None:
    review = AudioReview(
        duration_s=10, integrated_lufs=-14.0, true_peak_dbtp=-0.4, tempo_bpm=None, pulse_clarity=None,
        cues=[CueSync(at_s=1.0, status="OK", offset_ms=0.0, event=None)],
        median_abs_offset_ms=0.0, chance_within_tolerance=None,
    )
    assert review_problems(review) == ["pico real -0.4 dBTP acima de -1"]


def test_run_timeline_calls_earshot_offline_with_our_cuts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: dict = {}

    def fake_run(command, capture_output, text, env, check):  # noqa: ANN001
        seen["command"], seen["env"] = command, env
        Path(command[command.index("--out") + 1]).write_text(json.dumps(timeline_json()), encoding="utf-8")

        class Done:
            returncode, stderr = 0, ""

        return Done()

    monkeypatch.setattr(earshot.subprocess, "run", fake_run)
    out = tmp_path / "r.json"
    data = run_timeline(Path("/env/bin/python"), tmp_path / "final.mp4", [5.2, 15.6], out, threads=3)
    assert data["duration"] == 38.2
    assert seen["command"][:4] == ["/env/bin/python", "-m", "earshot", "timeline"]
    command = seen["command"]
    assert command[command.index("--cues") + 1] == "5.200,15.600"
    assert seen["env"]["EARSHOT_OFFLINE"] == "1" and seen["env"]["EARSHOT_THREADS"] == "3"


def test_run_timeline_failure_is_an_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    class Failed:
        returncode, stderr = 1, "earshot timeline: error: no such file"

    monkeypatch.setattr(earshot.subprocess, "run", lambda *a, **k: Failed())
    with pytest.raises(earshot.EarshotError, match="no such file"):
        run_timeline(Path("/env/bin/python"), tmp_path / "x.mp4", [], tmp_path / "r.json")
