"""Loudness integrada (LUFS, EBU R128) pelo filtro `ebur128` do ffmpeg: o volume final com trilha (ADR 030)
e a intensidade de uma faixa do catálogo."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

TARGET_LUFS = -14.0  # volume final de um vídeo com trilha
TOLERANCE_LU = 1.5
_INTEGRATED = re.compile(r"I:\s+(-?\d+(?:\.\d+)?) LUFS")
# Intensidade de 1 a 5 da faixa pela loudness integrada: limites em LUFS de cada degrau acima do 1.
INTENSITY_STEPS = (-30.0, -24.0, -19.0, -15.0)


class LoudnessError(RuntimeError):
    pass


def integrated_lufs(path: Path, *, input_args: list[str] | None = None) -> float:
    """Loudness integrada do áudio de `path`. `input_args` vem antes do `-i` (ex.: o demuxer concat)."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", *(input_args or []), "-i", str(path), "-map", "0:a:0",
         "-af", "ebur128", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    found = _INTEGRATED.findall(result.stderr)
    if result.returncode != 0 or not found:
        raise LoudnessError(f"ebur128 falhou em {path.name}: {result.stderr.strip()[-300:]}")
    return float(found[-1])  # o resumo do fim; as linhas do meio são parciais


def intensity(lufs: float) -> int:
    return 1 + sum(lufs > step for step in INTENSITY_STEPS)


def loudness_problem(lufs: float) -> str | None:
    """Alerta quando o volume final foge do alvo (ADR 030); a escuta do dono decide."""
    if abs(lufs - TARGET_LUFS) <= TOLERANCE_LU:
        return None
    return f"volume final {lufs:.1f} LUFS, alvo {TARGET_LUFS:.0f} ± {TOLERANCE_LU:g}"
