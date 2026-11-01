"""Constantes de bench; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class BenchConstants:
    BUSY_LOAD_PER_CPU: Final[float] = 0.25
    # sha256 de 64 MB leva centésimos numa CPU livre; muito mais = CPU estrangulada
    CPU_PROBE_SLOW_S: Final[float] = 0.3
    MAX_OUTPUT_TOKENS: Final[int] = 600
    RENDER_MODES: Final = (
        ("final-frio", False, True),
        ("final-cache", False, False),
        ("preview-frio", True, True),
    )
