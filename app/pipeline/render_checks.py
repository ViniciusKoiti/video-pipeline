"""Checks automáticos do render (CLAUDE.md §4), medidos no MP4 que saiu do motor.

Problema (bloqueia o gate 4 e vira pendência no `vp status`): o arquivo não abre no ffprobe, não tem trilha de
áudio, não tem a dimensão do perfil ou não dura o que a voz dura. Alerta (para a escuta do dono): volume fora
do alvo de −14 LUFS e silêncio longo dentro do vídeo. O resultado fica em `renders/checks-<render>.json`, com
o `sha256` do MP4 conferido: outro arquivo no lugar invalida a conferência.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.media.loudness import LoudnessError, integrated_lufs, loudness_problem
from app.media.pauses import SplitError, silences
from app.media.probe import ProbeError, duration_ms, probe_streams
from app.pipeline.atomic_files import write_atomic
from app.pipeline.constants.gates_constants import GatesConstants
from app.pipeline.constants.render_checks_constants import RenderChecksConstants as Constants
from app.pipeline.file_hash import sha256_file
from app.pipeline.models.render_checks import RenderChecks
from app.pipeline.ports import ManifestStore


def inspect_render(
    path: Path, *, render: str, expected_width: int, expected_height: int, expected_ms: int, now: datetime
) -> RenderChecks:
    """Mede o MP4 e classifica o que achou em problemas e alertas."""
    try:
        streams = probe_streams(path)
        total = duration_ms(path)
    except ProbeError as error:
        return RenderChecks(
            render=render, checked_at=now, opens=False, has_audio=False, expected_width=expected_width,
            expected_height=expected_height, expected_ms=expected_ms,
            problems=[f"não abre no ffprobe: {error}"],
        )
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    width = int(str(video["width"])) if video is not None else None
    height = int(str(video["height"])) if video is not None else None
    problems = _problems(has_audio, width, height, total, expected_width, expected_height, expected_ms)
    lufs, found, warnings = _audio_review(path) if has_audio else (None, [], [])
    return RenderChecks(
        render=render, sha256=sha256_file(path), checked_at=now, opens=True, has_audio=has_audio,
        width=width, height=height, expected_width=expected_width, expected_height=expected_height,
        duration_ms=total, expected_ms=expected_ms, lufs=lufs, long_silences_ms=found,
        problems=problems, warnings=warnings,
    )


def _problems(
    has_audio: bool, width: int | None, height: int | None, total: int,
    expected_width: int, expected_height: int, expected_ms: int,
) -> list[str]:
    problems = []
    if not has_audio:
        problems.append("sem trilha de áudio")
    if (width, height) != (expected_width, expected_height):
        problems.append(f"dimensão {width}×{height}, o perfil pede {expected_width}×{expected_height}")
    if abs(total - expected_ms) > Constants.DURATION_TOLERANCE_MS:
        problems.append(
            f"duração {total / 1000:.2f} s, a voz dura {expected_ms / 1000:.2f} s "
            f"(tolerância {Constants.DURATION_TOLERANCE_MS / 1000:.1f} s)"
        )
    return problems


def _audio_review(path: Path) -> tuple[float | None, list[tuple[int, int]], list[str]]:
    """Volume integrado e silêncios longos; o que não dá para medir vira alerta, nunca para o render."""
    warnings: list[str] = []
    lufs: float | None = None
    try:
        lufs = integrated_lufs(path)
        if (problem := loudness_problem(lufs)) is not None:
            warnings.append(problem)
    except LoudnessError as error:
        warnings.append(f"volume não medido: {error}")
    found: list[tuple[int, int]] = []
    try:
        quiet = silences(path, noise_db=Constants.SILENCE_NOISE_DB, min_s=Constants.SILENCE_MIN_S)
        found = [(round(start * 1000), round(end * 1000)) for start, end in quiet]
    except SplitError as error:
        warnings.append(f"silêncio não medido: {error}")
    warnings += [f"silêncio de {(end - start) / 1000:.1f} s aos {start / 1000:.1f} s" for start, end in found]
    return lufs, found, warnings


def checks_name(render: str) -> str:
    return Constants.FILE_PATTERN.format(stem=Path(render).stem)


def write_render_checks(store: ManifestStore, episode_id: str, checks: RenderChecks) -> Path:
    path = store.path(episode_id, checks_name(checks.render))
    write_atomic(path, (checks.model_dump_json(indent=2) + "\n").encode("utf-8"))
    return path


def read_render_checks(store: ManifestStore, episode_id: str, render: str) -> RenderChecks | None:
    """A conferência gravada para `render`, ou nada; arquivo fora do contrato levanta `ValueError`."""
    path = store.path(episode_id, checks_name(render))
    if not path.is_file():
        return None
    return RenderChecks.model_validate_json(path.read_text(encoding="utf-8"))


def stamped_render(store: ManifestStore, episode_id: str) -> str | None:
    """O render que o gate 4 carimba: o final, senão a prévia."""
    return next((r for r in GatesConstants.RENDERS if store.path(episode_id, r).is_file()), None)


def render_problems(store: ManifestStore, episode_id: str) -> list[str]:
    """Para o gate 4: os problemas da conferência do render carimbável. Sem conferência gravada (render
    anterior a este check), nada; MP4 trocado depois dela é problema."""
    render = stamped_render(store, episode_id)
    if render is None:
        return []
    try:
        checks = read_render_checks(store, episode_id, render)
    except ValueError as error:
        return [f"{checks_name(render)} fora do contrato: {str(error)[:160]}"]
    if checks is None:
        return []
    if checks.sha256 and checks.sha256 != sha256_file(store.path(episode_id, render)):
        return [f"{render} mudou depois da conferência; rode `vp render` de novo"]
    return list(checks.problems)


def render_pending(store: ManifestStore, episode_id: str) -> list[str]:
    """Para as pendências do `vp status`."""
    problems = render_problems(store, episode_id)
    return [f"render com {len(problems)} problema(s) na conferência"] if problems else []


def status_line(store: ManifestStore, episode_id: str) -> str | None:
    """Uma linha do `vp status`, quando há conferência gravada para o render carimbável."""
    render = stamped_render(store, episode_id)
    if render is None:
        return None
    try:
        checks = read_render_checks(store, episode_id, render)
    except ValueError:
        return f"{'render':6}{render:32} conferência fora do contrato (apague e rode `vp render`)"
    if checks is None:
        return f"{'render':6}{render:32} sem conferência (anterior aos checks; rode `vp render`)"
    problems = render_problems(store, episode_id)
    state = "ok" if not problems else f"{len(problems)} problema(s)"
    volume = f"{checks.lufs:.1f} LUFS" if checks.lufs is not None else "sem volume"
    return (
        f"{'render':6}{render:32} {'conferido':17} {checks.checked_at:%Y-%m-%d %H:%M} {volume} · {state}"
        + (f", {len(checks.warnings)} alerta(s)" if checks.warnings else "")
    )


def summary_lines(checks: RenderChecks) -> list[str]:
    """O que o `vp render` imprime depois de medir."""
    if not checks.opens:
        return ["conferência: 1 problema(s)", *(f"  problema: {p}" for p in checks.problems)]
    head = "ok" if checks.ok else f"{len(checks.problems)} problema(s)"
    volume = f"{checks.lufs:.1f} LUFS" if checks.lufs is not None else "sem volume"
    seconds = (checks.duration_ms or 0) / 1000
    lines = [
        f"conferência: {head}; áudio {'sim' if checks.has_audio else 'não'}; {checks.width}×{checks.height}; "
        f"{seconds:.1f} s (voz {checks.expected_ms / 1000:.1f} s); volume {volume}"
    ]
    lines += [f"  problema: {p}" for p in checks.problems]
    lines += [f"  alerta: {w}" for w in checks.warnings]
    return lines
