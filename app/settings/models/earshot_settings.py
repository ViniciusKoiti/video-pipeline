from __future__ import annotations

from pathlib import Path

from pydantic import Field

from app.settings.models._settings_model import _Model


class EarshotSettings(_Model):
    """Conferência de áudio com o earshot (ADR 035, emenda): o Python do ambiente dele vem do .env."""

    python: Path | None = None  # EARSHOT_PYTHON: o Python do ambiente em que o earshot está instalado
    threads: int = Field(default=4, gt=0)  # threads do torch; a máquina limitada pede menos
