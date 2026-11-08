"""Onde a fala começa e termina dentro de um WAV (RF7; eram `speech_bounds` e `bounds_from_log` de
`shorts_tec.py`): o `silencedetect` do ffmpeg acha os silêncios das pontas e a fala fica entre eles."""

from __future__ import annotations

import subprocess
from pathlib import Path

from app.errors import PipelineError
from app.media.constants.speech_bounds_constants import SpeechBoundsConstants as Constants
from app.media.probe import duration_ms


class SpeechBoundsError(PipelineError, RuntimeError):
    pass


def bounds_from_log(log: str, total: float, breath: float = Constants.BREATH_S) -> tuple[float, float]:
    """Onde a fala começa e termina, pelo `silencedetect` do ffmpeg: um silêncio que começa no zero adianta o
    começo; um que termina no fim do arquivo antecipa o fim. Sem silêncio nas pontas, o arquivo inteiro."""
    starts = [float(x) for x in Constants.SILENCE_START.findall(log)]
    ends = [float(x) for x in Constants.SILENCE_END.findall(log)]
    edge = Constants.EDGE_TOLERANCE_S
    begin, end = 0.0, total
    for s, e in zip(starts, ends, strict=False):
        if s <= edge:
            begin = max(0.0, e - breath)
        if e >= total - edge:
            end = min(total, s + breath)
    if len(starts) > len(ends) and starts[-1] > begin:  # silêncio aberto até o fim do arquivo
        end = min(total, starts[-1] + breath)
    return (begin, end) if end > begin else (0.0, total)


def speech_bounds(path: Path) -> tuple[float, float]:
    """A fala de um WAV, em segundos desde o início: `(começo, fim)`."""
    detect = f"silencedetect=noise={Constants.NOISE_DB}dB:d={Constants.EDGE_SILENCE_S}"
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", detect, "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SpeechBoundsError(f"ffmpeg não leu {path.name}: {result.stderr.strip()[-200:]}")
    return bounds_from_log(result.stderr, duration_ms(path) / 1000)
