"""Constantes do comando `vp sources`; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class SourcesCommandConstants:
    # tempo máximo de uma baixa de fonte, em segundos
    DOWNLOAD_TIMEOUT_S: Final[int] = 120
