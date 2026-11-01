"""Loudness integrada (LUFS, EBU R128) pelo filtro `ebur128` do ffmpeg: o volume final com trilha (ADR 030)
e a intensidade de uma faixa do catálogo."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

from app.media.constants.loudness_constants import LoudnessConstants

# Intensidade de 1 a 5 da faixa pela loudness integrada: limites em LUFS de cada degrau acima do 1.


class LoudnessError(RuntimeError):
    pass


def integrated_lufs(path: Path, *, input_args: Sequence[str] | None = None) -> float:
    """Loudness integrada do áudio de `path`. `input_args` vem antes do `-i` (ex.: o demuxer concat)."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", *(input_args or []), "-i", str(path), "-map", "0:a:0",
         "-af", "ebur128", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    found = LoudnessConstants._INTEGRATED.findall(result.stderr)
    if result.returncode != 0 or not found:
        raise LoudnessError(f"ebur128 falhou em {path.name}: {result.stderr.strip()[-300:]}")
    return float(found[-1])  # o resumo do fim; as linhas do meio são parciais


def intensity(lufs: float) -> int:
    return 1 + sum(lufs > step for step in LoudnessConstants.INTENSITY_STEPS)


def loudness_problem(lufs: float) -> str | None:
    """Alerta quando o volume final foge do alvo (ADR 030); a escuta do dono decide."""
    if abs(lufs - LoudnessConstants.TARGET_LUFS) <= LoudnessConstants.TOLERANCE_LU:
        return None
    return (
        f'volume final {lufs:.1f} LUFS, alvo {LoudnessConstants.TARGET_LUFS:.0f} ± '
        f'{LoudnessConstants.TOLERANCE_LU:g}'
    )
