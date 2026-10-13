"""`vp bench`: máquina, LLM e TTS medidos pelas portas (CLAUDE.md §3, etapa 5).

Mede o que o pipeline vai usar de fato; a comparação de provedores (etapa 29) reaproveita este código.
Uma falha de provedor vira registro no relatório, não interrompe as outras medições.
"""

from __future__ import annotations

import hashlib
import os
import platform
import resource
import shutil
import tempfile
import time
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from app.media.probe import duration_ms
from app.pipeline import bench_data
from app.pipeline.ports import Context
from app.pipeline.schemas import EpisodeManifest
from app.providers.errors import ProviderError
from app.providers.text.base import TextRequest
from app.providers.tts.base import SpeechRequest

BUSY_LOAD_PER_CPU = 0.25
CPU_PROBE_SLOW_S = 0.3  # sha256 de 64 MB leva centésimos numa CPU livre; muito mais = CPU estrangulada
MAX_OUTPUT_TOKENS = 600

Progress = Callable[[str], None]


class Machine(BaseModel):
    cpu_model: str
    cpus: int
    mem_total_mb: int
    mem_available_mb: int
    load_1m: float
    python: str
    cpu_probe_s: float = 0.0  # tempo da sonda de CPU (sha256 de 64 MB)
    busy: bool


class LlmRun(BaseModel):
    provider: str
    model: str
    run: int
    prompt_sha256: str = ""  # relatórios antigos não registravam o prompt
    ok: bool
    error: str = ""
    wall_s: float
    input_tokens: int = 0
    cached_input_tokens: int | None = None
    output_tokens: int = 0
    load_s: float | None = None
    prompt_tok_s: float | None = None
    generation_tok_s: float | None = None
    claims: int = 0
    unknown_excerpts: list[str] = []
    mem_available_mb_after: int = 0
    output: bench_data.BenchScript | None = None  # texto gerado, para avaliação humana de fidelidade (§7)


class TtsRun(BaseModel):
    provider: str
    voice: str = ""
    run: int
    ok: bool
    error: str = ""
    wall_s: float
    audio_s: float = 0.0
    rtf: float | None = None  # segundos de síntese por segundo de áudio
    seconds_per_audio_minute: float | None = None


class RenderRun(BaseModel):
    engine: str
    mode: str  # final-frio | final-cache | preview-frio
    ok: bool
    error: str = ""
    wall_s: float
    video_s: float = 0.0
    width: int = 0
    height: int = 0
    output_mb: float = 0.0
    realtime_factor: float | None = None  # segundos de vídeo por segundo de render (> 1 = mais rápido)
    peak_child_rss_mb: int = 0  # maior processo filho (ffmpeg) medido até aqui


class BenchReport(BaseModel):
    created_at: datetime
    machine: Machine
    warnings: list[str]
    llm: list[LlmRun]
    tts: list[TtsRun]
    render: list[RenderRun] = []
    peak_rss_mb: int  # deste processo (inclui o Kokoro); o Ollama roda em outro processo


def cpu_probe() -> float:
    """Carga fixa e curta: detecta CPU limitada (energia, temperatura) que a média de carga não mostra."""
    data = bytes(64 * 1024 * 1024)
    start = time.perf_counter()
    hashlib.sha256(data).hexdigest()
    return round(time.perf_counter() - start, 3)


def read_machine(proc: Path = Path("/proc"), probe: Callable[[], float] = cpu_probe) -> Machine:
    meminfo = (proc / "meminfo").read_text().splitlines()
    total_kb = next(int(line.split()[1]) for line in meminfo if line.startswith("MemTotal:"))
    cpu_model = next(
        (
            line.split(":", 1)[1].strip()
            for line in (proc / "cpuinfo").read_text().splitlines()
            if line.startswith("model name")
        ),
        platform.processor() or "desconhecido",
    )
    cpus = os.cpu_count() or 1
    load = float((proc / "loadavg").read_text().split()[0])
    probe_s = probe()
    return Machine(
        cpu_model=cpu_model,
        cpus=cpus,
        mem_total_mb=total_kb // 1024,
        mem_available_mb=_available_mb(proc),
        load_1m=load,
        python=platform.python_version(),
        cpu_probe_s=probe_s,
        busy=load / cpus > BUSY_LOAD_PER_CPU or probe_s > CPU_PROBE_SLOW_S,
    )


def _available_mb(proc: Path) -> int:
    for line in (proc / "meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    return 0


def _rate(tokens: int, ms: int | None) -> float | None:
    return round(tokens / (ms / 1000), 2) if ms else None


def bench_llm(context: Context, model: str | None, run: int, proc: Path = Path("/proc")) -> LlmRun:
    provider = context.text.info.name
    request = TextRequest(
        prompt=bench_data.prompt(run),
        output=bench_data.BenchScript,
        system=bench_data.SYSTEM,
        max_tokens=MAX_OUTPUT_TOKENS,
        model=model,
    )
    prompt_sha256 = hashlib.sha256(f"{request.system}\n\n{request.prompt}".encode()).hexdigest()
    start = time.perf_counter()
    try:
        result = context.text.generate_json(request)
    except ProviderError as error:
        return LlmRun(
            provider=provider,
            model=model or "padrão",
            run=run,
            prompt_sha256=prompt_sha256,
            ok=False,
            error=f"{error.reason}: {error}",
            wall_s=round(time.perf_counter() - start, 1),
            mem_available_mb_after=_available_mb(proc),
        )
    usage = result.usage
    known = {excerpt_id for excerpt_id, _ in bench_data.EXCERPTS}
    cited = {e for claim in result.data.claims for e in claim.excerpt_ids}
    return LlmRun(
        provider=provider,
        model=result.model,
        run=run,
        prompt_sha256=prompt_sha256,
        ok=True,
        wall_s=round(time.perf_counter() - start, 1),
        input_tokens=usage.input_tokens,
        cached_input_tokens=usage.cached_input_tokens,
        output_tokens=usage.output_tokens,
        load_s=None if usage.load_ms is None else round(usage.load_ms / 1000, 1),
        prompt_tok_s=_rate(usage.input_tokens, usage.prompt_ms),
        generation_tok_s=_rate(usage.output_tokens, usage.generation_ms),
        claims=len(result.data.claims),
        unknown_excerpts=sorted(cited - known),
        mem_available_mb_after=_available_mb(proc),
        output=result.data,
    )


def bench_tts(context: Context, run: int, workdir: Path) -> TtsRun:
    provider = context.tts.info.name
    out = workdir / f"tts-run{run}.wav"
    start = time.perf_counter()
    try:
        result = context.tts.synthesize_speech(SpeechRequest(text=bench_data.NARRATION, out_path=out))
    except ProviderError as error:
        return TtsRun(provider=provider, run=run, ok=False, error=f"{error.reason}: {error}",
                      wall_s=round(time.perf_counter() - start, 1))
    wall = time.perf_counter() - start
    audio_s = duration_ms(out) / 1000
    rtf = wall / audio_s
    return TtsRun(
        provider=provider,
        voice=result.voice,
        run=run,
        ok=True,
        wall_s=round(wall, 1),
        audio_s=round(audio_s, 1),
        rtf=round(rtf, 2),
        seconds_per_audio_minute=round(rtf * 60, 1),
    )


RENDER_MODES = (("final-frio", False, True), ("final-cache", False, False), ("preview-frio", True, True))


def bench_render(context: Context, episode_dir: Path) -> list[RenderRun]:
    """Renderiza o episódio pela porta RenderEngine: final sem cache, final com cache e prévia."""
    episode = EpisodeManifest.model_validate_json((episode_dir / "episode.json").read_text())
    renderer = context.renderer(episode.format)
    engine = renderer.info.name
    out_dir = context.settings.data_dir / "benchmarks" / "renders" / engine
    runs = []
    for mode, preview, cold in RENDER_MODES:
        out = out_dir / f"{episode.episode_id}-{'preview' if preview else 'final'}.mp4"
        if cold:
            shutil.rmtree(out_dir / f".segments-{'preview' if preview else 'final'}", ignore_errors=True)
        start = time.perf_counter()
        try:
            result = renderer.render(episode, episode_dir, out, preview=preview)
        except (ProviderError, RuntimeError) as error:
            runs.append(RenderRun(engine=engine, mode=mode, ok=False, error=str(error)[:300],
                                  wall_s=round(time.perf_counter() - start, 1)))
            continue
        wall = time.perf_counter() - start
        video_s = result.duration_ms / 1000
        runs.append(RenderRun(
            engine=engine,
            mode=mode,
            ok=True,
            wall_s=round(wall, 1),
            video_s=round(video_s, 2),
            width=result.width,
            height=result.height,
            output_mb=round(result.path.stat().st_size / 1e6, 1),
            realtime_factor=round(video_s / wall, 2) if wall else None,
            peak_child_rss_mb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss // 1024,
        ))
    return runs


def run_bench(
    context: Context,
    *,
    models: Sequence[str | None],
    runs: int,
    now: Callable[[], datetime],
    include_llm: bool = True,
    include_tts: bool = True,
    render_dir: Path | None = None,
    progress: Progress = lambda message: None,
    proc: Path = Path("/proc"),
    probe: Callable[[], float] = cpu_probe,
) -> tuple[BenchReport, Path]:
    machine = read_machine(proc, probe)
    warnings = []
    if machine.busy:
        warnings.append(
            f"CPU ocupada ou limitada no início (load {machine.load_1m} para {machine.cpus} CPUs, "
            f"sonda {machine.cpu_probe_s}s): os tempos podem sair piores que o normal"
        )
        progress("aviso: " + warnings[-1])
    llm: list[LlmRun] = []
    if include_llm:
        for model in models:
            for run in range(1, runs + 1):
                progress(f"LLM {model or 'padrão'}: execução {run}/{runs}")
                llm.append(bench_llm(context, model, run, proc))
    tts: list[TtsRun] = []
    if include_tts and context.tts.info.remote:
        # O bench mede a máquina; voz remota gastaria a cota de um serviço externo sem pedido (§14).
        progress(f"TTS pulado: {context.tts.info.name} é remoto (o bench mede só voz local)")
        include_tts = False
    if include_tts:
        with tempfile.TemporaryDirectory(prefix="vp-bench-") as tmp:
            for run in range(1, runs + 1):
                progress(f"TTS: execução {run}/{runs}")
                tts.append(bench_tts(context, run, Path(tmp)))
    render: list[RenderRun] = []
    if render_dir is not None:
        progress("render pelo motor do formato do episódio: final sem cache, final com cache e prévia")
        render = bench_render(context, render_dir)
    created_at = now()
    report = BenchReport(
        created_at=created_at,
        machine=machine,
        warnings=warnings,
        llm=llm,
        tts=tts,
        render=render,
        peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
    )
    out = context.settings.data_dir / "benchmarks" / f"machine-{created_at:%Y%m%d-%H%M%S}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.model_dump_json(indent=2) + "\n")
    return report, out


def summary(report: BenchReport) -> list[str]:
    lines = [f"{report.machine.cpu_model} · {report.machine.cpus} CPUs · {report.machine.mem_total_mb} MB"]
    for r in report.llm:
        if r.ok:
            invalid = f" · ids inválidos {r.unknown_excerpts}" if r.unknown_excerpts else ""
            lines.append(
                f"LLM {r.model} #{r.run}: gera {r.generation_tok_s} tok/s · lê {r.prompt_tok_s} tok/s · "
                f"{r.wall_s}s · {r.claims} claims{invalid}"
            )
        else:
            lines.append(f"LLM {r.model} #{r.run}: FALHOU ({r.error})")
    for t in report.tts:
        lines.append(
            f"TTS {t.provider} #{t.run}: RTF {t.rtf} · {t.seconds_per_audio_minute}s por minuto de áudio"
            if t.ok
            else f"TTS {t.provider} #{t.run}: FALHOU ({t.error})"
        )
    for r in report.render:
        lines.append(
            f"render {r.engine} {r.mode}: {r.wall_s}s para {r.video_s}s de vídeo ({r.realtime_factor}x) · "
            f"{r.width}x{r.height} · {r.output_mb} MB · ffmpeg até {r.peak_child_rss_mb} MB"
            if r.ok
            else f"render {r.engine} {r.mode}: FALHOU ({r.error})"
        )
    return lines + [f"aviso: {w}" for w in report.warnings]
