"""Corta a narração de várias cenas, gerada numa chamada só, nas pausas longas entre elas (ADR 012).

A voz recebe as cenas separadas por uma pausa longa; aqui o `silencedetect` do ffmpeg acha os silêncios, as
N-1 pausas mais longas viram as fronteiras entre N cenas e cada cena é recortada com uma folga curta. Se as
fronteiras não forem claramente mais longas que as pausas de respiração dentro das frases, o corte é recusado:
melhor gerar de novo do que pôr a frase de uma cena na outra.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from app.media.probe import duration_ms

NOISE_DB = -40  # abaixo disto é silêncio
MIN_SILENCE_S = 0.2  # silêncios mais curtos nem entram na conta
MIN_BOUNDARY_S = 0.6  # uma fronteira entre cenas dura pelo menos isto
MARGIN = 1.3  # a fronteira mais curta é 30% maior que a pausa mais longa dentro das cenas
LEAD_S = 0.2  # silêncio mantido antes da fala de cada cena (o Kokoro deixa ~0,2 s)
TAIL_S = 0.15  # silêncio mantido depois da fala


class SplitError(RuntimeError):
    pass


def silences(path: Path) -> list[tuple[float, float]]:
    """Silêncios internos (início, fim) em segundos; os das pontas do arquivo ficam de fora."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
         "-af", f"silencedetect=noise={NOISE_DB}dB:d={MIN_SILENCE_S}", "-f", "null", "-"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise SplitError(f"ffmpeg não leu {path.name}: {result.stderr.strip()[-200:]}")
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", result.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", result.stderr)]
    total = duration_ms(path) / 1000
    return [(s, e) for s, e in zip(starts, ends, strict=False) if s > 0.05 and e < total - 0.05]


def boundaries(found: list[tuple[float, float]], parts: int) -> list[tuple[float, float]]:
    """As `parts - 1` pausas mais longas, em ordem no tempo; recusa se não se destacam das outras."""
    if parts < 2:
        return []
    if len(found) < parts - 1:
        raise SplitError(f"{len(found)} pausas para separar {parts} cenas")
    by_length = sorted(found, key=lambda s: s[1] - s[0], reverse=True)
    chosen, rest = by_length[: parts - 1], by_length[parts - 1 :]
    shortest = min(e - s for s, e in chosen)
    longest_rest = max((e - s for s, e in rest), default=0.0)
    if shortest < MIN_BOUNDARY_S or shortest < longest_rest * MARGIN:
        raise SplitError(
            f"fronteira de {shortest:.2f} s não se destaca da pausa interna de {longest_rest:.2f} s"
        )
    return sorted(chosen)


def split_at_pauses(path: Path, outs: list[Path]) -> list[Path]:
    """Grava uma cena em cada `outs`, na ordem; WAV PCM 16 bits, mesma taxa do original."""
    cuts = boundaries(silences(path), len(outs))
    total = duration_ms(path) / 1000
    starts = [0.0] + [e - LEAD_S for _, e in cuts]
    ends = [s + TAIL_S for s, _ in cuts] + [total]
    for out, start, end in zip(outs, starts, ends, strict=True):
        out.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(path),
             "-ss", f"{max(start, 0):.3f}", "-to", f"{end:.3f}", "-c:a", "pcm_s16le", str(out)],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            raise SplitError(f"ffmpeg não cortou {out.name}: {result.stderr.strip()[-200:]}")
    return outs
