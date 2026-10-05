"""Envelope de energia da fala, um valor por quadro, para a boca do apresentador (ADR 013)."""

from __future__ import annotations

import sys
import wave
from array import array
from pathlib import Path

PERCENTILE = 0.95  # o nível que vale 1: picos isolados não achatam o resto da cena


def mouth_levels(wav: Path, fps: int, frames: int) -> list[float]:
    """RMS de cada quadro, de 0 a 1, normalizado pelo percentil 95 da própria cena, com `frames` valores
    (completa com 0 ou corta). Só WAV PCM de 16 bits; mistura os canais pelo primeiro."""
    with wave.open(str(wav)) as reader:
        if reader.getsampwidth() != 2:
            raise ValueError(f"{wav.name}: esperado WAV de 16 bits, veio {8 * reader.getsampwidth()}")
        channels, rate = reader.getnchannels(), reader.getframerate()
        raw = reader.readframes(reader.getnframes())
    samples = array("h")
    samples.frombytes(raw)
    if sys.byteorder == "big":
        samples.byteswap()
    mono = samples[::channels]
    step = rate / fps
    rms = []
    for i in range(frames):
        chunk = mono[round(i * step) : round((i + 1) * step)]
        rms.append((sum(v * v for v in chunk) / len(chunk)) ** 0.5 / 32768 if chunk else 0.0)
    reference = sorted(rms)[int(len(rms) * PERCENTILE)] if rms else 0.0
    if reference <= 0:
        return [0.0] * frames
    return [round(min(1.0, level / reference), 3) for level in rms]
