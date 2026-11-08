"""Valores fixos do motor FFmpeg; parâmetros configuráveis continuam no motor e nos modelos."""

import re
from typing import Final


class FfmpegConstants:
    ENGINE_VERSION: Final[str] = "2"  # mudar invalida segmentos (v2: matriz e marcação bt709)
    FIT_MIN_ASPECT: Final[float] = 1.45
    SRT_TIME: Final[re.Pattern[str]] = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d\d\d)")
    CONCAT: Final[tuple[str, ...]] = ("-f", "concat", "-safe", "0")
    AUDIO_VERSION: Final[str] = "2"  # mudar invalida o áudio em cache (v2: voz a −14 LUFS também sem trilha)
    # Ducking (ADR 030): a trilha baixa enquanto a voz fala.
    DUCKING: Final[str] = "sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500"
    LIMITER: Final[str] = "alimiter=limit=0.89:level=false"  # teto de ~-1 dBFS após o ganho de loudness
