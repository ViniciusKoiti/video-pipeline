"""Constantes da conferência do render (checks automáticos do §4); dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class RenderChecksConstants:
    # o resultado fica ao lado do MP4: renders/checks-final.json ou renders/checks-preview.json
    FILE_PATTERN: Final[str] = "renders/checks-{stem}.json"
    # duração do MP4 contra o fim da última cena: a voz manda no tempo (§9)
    DURATION_TOLERANCE_MS: Final[int] = 500
    # silêncio longo dentro do vídeo é alerta, não problema: pode ser pausa de leitura planejada
    SILENCE_NOISE_DB: Final[float] = -45.0
    SILENCE_MIN_S: Final[float] = 3.0
