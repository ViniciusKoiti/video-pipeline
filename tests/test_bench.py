from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

import app.cli
from app.cli import main
from app.pipeline.bench import BenchReport, run_bench, summary
from app.pipeline.bench_data import EXCERPTS, BenchClaim, BenchScript, prompt
from tests.fakes import FakeContext, FakeText, InMemoryStore, make_root, make_settings

NOW = datetime(2026, 9, 25, 14, 30, tzinfo=UTC)


def script(*excerpt_ids: str) -> str:
    claims = [BenchClaim(text=f"claim {e}", excerpt_ids=[e]) for e in excerpt_ids]
    return BenchScript(narration="The Halcyon left Aldermoor.", claims=claims).model_dump_json()


def fake_proc(tmp_path: Path, load: str = "0.50") -> Path:
    proc = tmp_path / "proc"
    proc.mkdir()
    (proc / "meminfo").write_text("MemTotal:       12000000 kB\nMemAvailable:    8000000 kB\n")
    (proc / "cpuinfo").write_text("processor\t: 0\nmodel name\t: Test CPU 5700U\n")
    (proc / "loadavg").write_text(f"{load} 0.40 0.30 1/100 1234\n")
    return proc


def context(tmp_path: Path, responses: list[str]) -> FakeContext:
    return FakeContext(
        settings=make_settings(tmp_path),
        store=InMemoryStore(tmp_path),
        text=FakeText(responses),
    )


def test_prompt_is_about_1000_tokens_and_changes_per_run() -> None:
    words = len(prompt(1).split())
    assert 650 <= words <= 900  # ~1000 tokens
    assert prompt(1) != prompt(2)  # evita reaproveitar o cache do prompt
    assert len(EXCERPTS) == 16


def test_bench_measures_every_model_and_writes_json(tmp_path: Path) -> None:
    ctx = context(tmp_path, [script("E1", "E4"), script("E2"), script("E3", "E99"), script("E5")])
    report, path = run_bench(ctx, models=["m1", "m2"], runs=2, now=lambda: NOW, proc=fake_proc(tmp_path))
    assert [(r.model, r.run, r.ok) for r in report.llm] == [
        ("m1", 1, True), ("m1", 2, True), ("m2", 1, True), ("m2", 2, True),
    ]
    assert report.llm[2].unknown_excerpts == ["E99"]  # citação fora dos trechos
    assert report.llm[0].output is not None and report.llm[0].output.narration.startswith("The Halcyon")
    assert report.machine.cpu_model == "Test CPU 5700U"
    assert (report.machine.mem_total_mb, report.machine.mem_available_mb) == (11718, 7812)
    assert len(report.tts) == 2 and all(t.ok and t.audio_s > 0 and t.rtf is not None for t in report.tts)
    assert path == ctx.settings.data_dir / "benchmarks" / "machine-20260925-143000.json"
    assert BenchReport.model_validate(json.loads(path.read_text())) == report


def test_provider_failure_is_recorded_and_bench_continues(tmp_path: Path) -> None:
    ctx = context(tmp_path, ['{"not": "a script"}', script("E1")])
    report, _ = run_bench(
        ctx, models=["m1"], runs=2, now=lambda: NOW, include_tts=False, proc=fake_proc(tmp_path)
    )
    assert [r.ok for r in report.llm] == [False, True]
    assert report.llm[0].error.startswith("invalid_output")
    assert any("FALHOU" in line for line in summary(report))


def test_throttled_cpu_is_warned_even_with_low_load(tmp_path: Path) -> None:
    report, _ = run_bench(
        context(tmp_path, []), models=[], runs=1, now=lambda: NOW, include_tts=False,
        proc=fake_proc(tmp_path, load="0.10"), probe=lambda: 2.5,
    )
    assert report.machine.busy and "sonda 2.5s" in report.warnings[0]


def test_busy_machine_is_warned_not_blocked(tmp_path: Path) -> None:
    messages: list[str] = []
    report, _ = run_bench(
        context(tmp_path, []), models=[], runs=1, now=lambda: NOW, include_tts=False,
        progress=messages.append, proc=fake_proc(tmp_path, load="999"),
    )
    assert report.machine.busy and report.warnings
    assert messages[0].startswith("aviso: CPU ocupada")


def test_cli_bench_runs_through_the_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    ctx = context(tmp_path / "ctx", [script("E1")])
    monkeypatch.setattr(app.cli, "build_context", lambda root: ctx)
    monkeypatch.chdir(make_root(tmp_path / "project"))
    assert main(["bench", "--models", "qwen3:4b", "--runs", "1", "--skip-tts"]) == 0
    out = capsys.readouterr().out
    assert "LLM qwen3:4b #1" in out and "resultado:" in out
    assert ctx.text.requests[0].model == "qwen3:4b"


def test_render_bench_measures_cold_cached_and_preview(tmp_path: Path) -> None:
    fixture = Path(__file__).parent / "fixtures" / "episodes" / "engine-test"
    report, _ = run_bench(
        context(tmp_path, []), models=[], runs=1, now=lambda: NOW, include_tts=False,
        render_dir=fixture, proc=fake_proc(tmp_path),
    )
    assert [(r.mode, r.ok, r.width) for r in report.render] == [
        ("final-frio", True, 1920), ("final-cache", True, 1920), ("preview-frio", True, 1280),
    ]
    assert all(r.video_s == 52.52 and r.realtime_factor for r in report.render)
    assert any(line.startswith("render fake-render final-frio") for line in summary(report))
