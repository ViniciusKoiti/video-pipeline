"""Folha de escuta: os trechos suspeitos de várias falas num WAV só, separados por silêncio (ADR 062).

O dono ouve em um minuto o que a conferência apontou, em vez do vídeo inteiro. Cada trecho é cortado do WAV
da cena com uma folga antes e depois; a saída é mono a 48 kHz e só aparece inteira (arquivo temporário trocado
no fim). Falha do ffmpeg vira `ListeningSheetError`.
"""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

from app.errors import PipelineError

Clip = tuple[Path, int, int]  # WAV, início e fim do trecho em ms


class ListeningSheetError(PipelineError, RuntimeError):
    """O ffmpeg não conseguiu montar a folha de escuta."""


def sheet_filter(clips: Sequence[Clip], pad_ms: int, gap_ms: int) -> str:
    """O filtro do ffmpeg: cada entrada cortada no trecho com folga, e silêncio entre os trechos."""
    parts, labels = [], []
    for i, (_, start, end) in enumerate(clips):
        begin, finish = max(0, start - pad_ms) / 1000, (end + pad_ms) / 1000
        parts.append(
            f"[{i}:a]atrim=start={begin:.3f}:end={finish:.3f},asetpts=PTS-STARTPTS,"
            f"aresample=48000,aformat=channel_layouts=mono[c{i}]"
        )
        labels.append(f"[c{i}]")
        if i < len(clips) - 1:
            parts.append(f"anullsrc=r=48000:cl=mono,atrim=duration={gap_ms / 1000:.3f}[g{i}]")
            labels.append(f"[g{i}]")
    parts.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[out]")
    return ";".join(parts)


def build_sheet(clips: Sequence[Clip], out: Path, *, pad_ms: int, gap_ms: int) -> Path:
    if not clips:
        raise ListeningSheetError("folha de escuta sem trechos")
    partial = out.with_name(out.stem + ".partial.wav")
    inputs = [arg for wav, _, _ in clips for arg in ("-i", str(wav))]
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs,
        "-filter_complex", sheet_filter(clips, pad_ms, gap_ms), "-map", "[out]", str(partial),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        partial.unlink(missing_ok=True)
        raise ListeningSheetError(f"ffmpeg falhou na folha de escuta: {result.stderr.strip()[-400:]}")
    partial.replace(out)
    return out
