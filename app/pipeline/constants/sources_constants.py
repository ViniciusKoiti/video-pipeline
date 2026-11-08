"""Constantes do registro de fontes; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class SourcesConstants:
    # os primeiros bytes de um PDF; o resto é tratado como HTML
    PDF_MAGIC: Final[bytes] = b"%PDF-"
    # o id de uma fonte registrada, com o número que entra no próximo id
    ID: Final = re.compile(r"^source-(\d+)$")
