from __future__ import annotations

from pathlib import Path

from app.pipeline.models.model import Model


class PlacedSfx(Model):
    sound: str
    file: Path
    moment_s: float  # o que o som encontra
    start_s: float  # onde o arquivo começa na linha do tempo (nunca negativo)
    trim_s: float  # quanto cortar do começo do arquivo quando o início cairia antes de 0
    gain_db: float
    under_speech: bool
