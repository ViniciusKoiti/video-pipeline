"""Checks automáticos do render (CLAUDE.md §4): medição do MP4, arquivo gravado, `vp status` e gate 4."""

from __future__ import annotations

import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.pipeline.gates import GateError
from app.pipeline.models.render_checks import RenderChecks
from app.pipeline.render_checks import (
    checks_name,
    inspect_render,
    read_render_checks,
    render_pending,
    render_problems,
    status_line,
    summary_lines,
    write_render_checks,
)
from app.pipeline.schemas import Decision, Step
from tests.test_gates import EPISODE, decide, episode, rendered

NOW = datetime(2026, 11, 7, 22, 0, tzinfo=UTC)


def mp4(
    path: Path, *, width: int = 320, height: int = 180, seconds: float = 2.0, audio: bool = True,
    gain_db: float = 7.0, quiet: tuple[float, float] | None = None,
) -> Path:
    """Um MP4 sintético: cor chapada e um tom (o `sine` do ffmpeg sai a ~−21 LUFS; +7 dB dá ~−14); `quiet`
    cala o tom entre dois instantes."""
    video = f"color=c=black:s={width}x{height}:r=10:d={seconds}"
    command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", video]
    if audio:
        filters = f"volume={gain_db}dB"
        if quiet is not None:
            filters += f",volume=0:enable='between(t,{quiet[0]},{quiet[1]})'"
        command += ["-f", "lavfi", "-i", f"sine=frequency=440:sample_rate=48000:duration={seconds}",
                    "-af", filters, "-c:a", "aac"]
    command += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-shortest", str(path)]
    subprocess.run(command, check=True, capture_output=True)
    return path


def inspect(path: Path) -> RenderChecks:
    return inspect_render(
        path, render="renders/preview.mp4", expected_width=320, expected_height=180, expected_ms=2000, now=NOW
    )


def test_a_good_render_opens_has_audio_fits_the_profile_and_lasts_the_voice(tmp_path: Path) -> None:
    checks = inspect_render(
        mp4(tmp_path / "ok.mp4"), render="renders/final.mp4", expected_width=320, expected_height=180,
        expected_ms=2000, now=NOW,
    )
    assert checks.ok and checks.opens and checks.has_audio and (checks.width, checks.height) == (320, 180)
    assert checks.duration_ms is not None and abs(checks.duration_ms - 2000) <= 150
    assert checks.lufs is not None and -17 < checks.lufs < -11 and checks.long_silences_ms == []
    assert checks.sha256 and len(checks.sha256) == 64 and checks.render == "renders/final.mp4"
    head = "conferência: ok; áudio sim; 320×180; 2.0 s (voz 2.0 s); volume -1"
    assert summary_lines(checks)[0].startswith(head)


def test_missing_audio_wrong_size_and_wrong_duration_are_problems(tmp_path: Path) -> None:
    checks = inspect_render(
        mp4(tmp_path / "mudo.mp4", audio=False), render="renders/preview.mp4", expected_width=640,
        expected_height=360, expected_ms=3000, now=NOW,
    )
    assert not checks.ok and checks.lufs is None and checks.warnings == []
    assert checks.problems == [
        "sem trilha de áudio",
        "dimensão 320×180, o perfil pede 640×360",
        "duração 2.00 s, a voz dura 3.00 s (tolerância 0.5 s)",
    ]
    assert summary_lines(checks)[0].startswith("conferência: 3 problema(s)")
    assert summary_lines(checks)[1:] == [f"  problema: {p}" for p in checks.problems]


def test_a_quiet_file_and_a_long_silence_are_warnings_not_problems(tmp_path: Path) -> None:
    checks = inspect_render(
        mp4(tmp_path / "baixo.mp4", seconds=8.0, gain_db=-12.0, quiet=(2.0, 6.0)), render="renders/final.mp4",
        expected_width=320, expected_height=180, expected_ms=8000, now=NOW,
    )
    assert checks.ok and checks.lufs is not None and checks.lufs < -25
    assert any(w.startswith("volume final") for w in checks.warnings)
    [(start, end)] = checks.long_silences_ms
    assert 1800 <= start <= 2300 and 5800 <= end <= 6300
    assert any(re.fullmatch(r"silêncio de [34]\.\d s aos [12]\.\d s", w) for w in checks.warnings)
    assert [line for line in summary_lines(checks) if line.startswith("  alerta:")] == [
        f"  alerta: {w}" for w in checks.warnings
    ]


def test_a_file_that_does_not_open_is_a_problem(tmp_path: Path) -> None:
    broken = tmp_path / "quebrado.mp4"
    broken.write_bytes(b"isto nao e um mp4")
    checks = inspect(broken)
    assert not checks.opens and not checks.has_audio and len(checks.problems) == 1
    assert checks.problems[0].startswith("não abre no ffprobe")
    assert summary_lines(checks) == ["conferência: 1 problema(s)", f"  problema: {checks.problems[0]}"]


def test_checks_are_written_beside_the_render_and_block_gate_4_until_clean(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    preview = rendered(folder)
    checks = inspect_render(
        preview, render="renders/preview.mp4", expected_width=1280, expected_height=720, expected_ms=1000,
        now=NOW,
    )
    assert not checks.opens  # b"previa" não é um MP4
    path = write_render_checks(store, EPISODE, checks)
    assert path == folder / "renders" / "checks-preview.json" and checks_name("renders/final.mp4").endswith(
        "checks-final.json"
    )
    assert read_render_checks(store, EPISODE, "renders/preview.mp4") == checks
    assert render_problems(store, EPISODE) == checks.problems
    assert render_pending(store, EPISODE) == ["render com 1 problema(s) na conferência"]
    line = status_line(store, EPISODE) or ""
    assert line.startswith("render") and "2026-11-07 22:00 sem volume · 1 problema(s)" in line
    with pytest.raises(GateError, match="a conferência do render achou 1 problema"):
        decide(store, review, Step.PREVIEW, Decision.APPROVED)
    clean = mp4(folder / "renders" / "preview.mp4", width=1280, height=720, seconds=1.0)
    write_render_checks(
        store, EPISODE, inspect_render(
            clean, render="renders/preview.mp4", expected_width=1280, expected_height=720, expected_ms=1000,
            now=NOW,
        ),
    )
    assert render_problems(store, EPISODE) == [] and render_pending(store, EPISODE) == []
    decide(store, review, Step.PREVIEW, Decision.APPROVED)


def test_a_render_replaced_after_the_checks_is_a_problem_again(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    (folder / "renders").mkdir()
    clean = mp4(folder / "renders" / "preview.mp4", width=1280, height=720, seconds=1.0)
    write_render_checks(
        store, EPISODE, inspect_render(
            clean, render="renders/preview.mp4", expected_width=1280, expected_height=720, expected_ms=1000,
            now=NOW,
        ),
    )
    assert render_problems(store, EPISODE) == []
    rendered(folder, "preview.mp4", b"outro arquivo no lugar")
    changed = "renders/preview.mp4 mudou depois da conferência; rode `vp render` de novo"
    assert render_problems(store, EPISODE) == [changed]
    with pytest.raises(GateError, match="mudou depois da conferência"):
        decide(store, review, Step.PREVIEW, Decision.APPROVED)


def test_without_a_checks_file_nothing_changes_and_the_status_says_so(tmp_path: Path) -> None:
    store, review, folder = episode(tmp_path)
    assert status_line(store, EPISODE) is None and render_pending(store, EPISODE) == []
    rendered(folder)
    assert render_problems(store, EPISODE) == []
    line = status_line(store, EPISODE)
    assert line is not None and "sem conferência (anterior aos checks" in line
    decide(store, review, Step.PREVIEW, Decision.APPROVED)  # render anterior a este check: nada muda
    (folder / "renders" / "checks-preview.json").write_text("{nao e json")
    assert render_problems(store, EPISODE)[0].startswith("renders/checks-preview.json fora do contrato")
    assert "conferência fora do contrato" in (status_line(store, EPISODE) or "")
