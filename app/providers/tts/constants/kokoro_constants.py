"""Constantes de kokoro; dados fixos sem I/O."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final


class KokoroConstants:
    REPO_ID: Final[str] = "hexgrad/Kokoro-82M"
    SAMPLE_RATE: Final[int] = 24000
    # códigos do KPipeline: inglês americano, português do Brasil
    LANG_CODES: Final = MappingProxyType({"en": "a", "pt-BR": "p"})
