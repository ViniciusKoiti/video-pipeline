"""Constantes da fila do `vp imagens` (ADR 065); dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class ImageQueueConstants:
    ORDER_ID: Final = re.compile(r"^[a-z0-9][a-z0-9\-]{0,79}$")  # vira nome de arquivo: sem barra nem ponto
    SCENE_ID: Final = re.compile(r"^S\d{2,}$")
    LOG_FILE: Final[str] = "registro.jsonl"  # mesmo nome e formato do script antigo: pastas antigas continuam
    GENERATED: Final[str] = "gerada"
    FAILED: Final[str] = "falhou"
    MAX_CONSECUTIVE_FAILURES: Final[int] = 2  # duas seguidas: seletor quebrado, não azar
