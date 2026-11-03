"""Cópia nivelada de cada fala: duas passagens, cache pelo áudio bruto e política, original preservado."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path

from app.errors import PipelineError
from app.media.constants.voice_level_constants import VoiceLevelConstants as C
from app.media.models.voice_level_report import VoiceLevelReport
from app.media.probe import duration_ms
from app.media.wav import wav_is_valid


class VoiceLevelError(PipelineError, RuntimeError):
    pass


def level_policy() -> str:
    return f"loudnorm-v{C.VERSION}:{C.TARGET_LUFS}:{C.TRUE_PEAK_DBTP}:{C.LRA}:{C.SAMPLE_RATE}"


def _ffmpeg(source: Path, filters: str, output: list[str]) -> str:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-nostdin", "-n", "-i", str(source), "-af", filters, *output],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise VoiceLevelError(f"{source.name}: falha ao nivelar áudio: {result.stderr.strip()[-250:]}")
    return result.stderr


def _measure(source: Path, *, mono: bool = False) -> dict[str, float]:
    prefix = "aformat=channel_layouts=mono,pan=stereo|c0=c0|c1=c0," if mono else ""
    filters = f"{prefix}loudnorm=I={C.TARGET_LUFS}:TP={C.TRUE_PEAK_DBTP}:LRA={C.LRA}:print_format=json"
    log = _ffmpeg(source, filters, ["-f", "null", "-"])
    try:
        values, _ = json.JSONDecoder().raw_decode(log[log.rfind("{"):])
        stats = {key: float(values[key]) for key in (
            "input_i", "input_tp", "input_lra", "input_thresh", "target_offset"
        )}
    except (ValueError, KeyError, TypeError) as error:
        raise VoiceLevelError(f"{source.name}: medição de volume inválida") from error
    if not all(math.isfinite(value) for value in stats.values()):
        raise VoiceLevelError(f"{source.name}: falta fala mensurável para nivelar")
    return stats


def _cached(out: Path, digest: str) -> bool:
    if not wav_is_valid(out):
        return False
    try:
        report = VoiceLevelReport.model_validate_json(out.with_suffix(".json").read_text())
        return (
            report.source_sha256 == digest and report.policy == level_policy()
            and report.wav_sha256 == hashlib.sha256(out.read_bytes()).hexdigest()
        )
    except (OSError, ValueError):
        return False


def _generate(source: Path, out: Path, digest: str) -> None:
    measured = _measure(source, mono=True)
    filters = (
        f"aformat=channel_layouts=mono,pan=stereo|c0=c0|c1=c0,loudnorm=I={C.TARGET_LUFS}:"
        f"TP={C.TRUE_PEAK_DBTP}:LRA={C.LRA}:measured_I={measured['input_i']}:"
        f"measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:"
        f"measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:linear=true,"
        f"aresample={C.SAMPLE_RATE}"
    )
    with tempfile.TemporaryDirectory(dir=out.parent) as folder:
        partial = Path(folder) / "voice.wav"
        _ffmpeg(source, filters, ["-c:a", "pcm_s16le", str(partial)])
        actual = _measure(partial)
        if abs(actual["input_i"] - C.TARGET_LUFS) > C.TOLERANCE_LU:
            raise VoiceLevelError(f"{source.name}: volume nivelado fora do alvo")
        if actual["input_tp"] > C.TRUE_PEAK_DBTP + C.PEAK_TOLERANCE_DB:
            raise VoiceLevelError(f"{source.name}: pico do áudio nivelado acima do teto")
        if abs(duration_ms(source) - duration_ms(partial)) > C.DURATION_TOLERANCE_MS:
            raise VoiceLevelError(f"{source.name}: nivelamento alterou a duração da fala")
        report = VoiceLevelReport(
            source=source, source_sha256=digest, wav_sha256=hashlib.sha256(partial.read_bytes()).hexdigest(),
            policy=level_policy(), target_lufs=C.TARGET_LUFS, input_lufs=measured["input_i"],
            output_lufs=actual["input_i"], true_peak_dbtp=actual["input_tp"],
        )
        record = Path(folder) / "voice.json"
        record.write_text(report.model_dump_json(indent=2) + "\n")
        partial.replace(out)
        record.replace(out.with_suffix(".json"))


def level_voice(source: Path) -> Path:
    if not wav_is_valid(source):
        raise VoiceLevelError(f"{source.name}: WAV bruto ausente ou inválido")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    key = hashlib.sha256(f"{digest}|{level_policy()}".encode()).hexdigest()[:C.DIGEST_CHARS]
    out = source.parent / C.DIRECTORY / f"{source.stem}-{key}.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not _cached(out, digest):
        _generate(source, out, digest)
    return out
