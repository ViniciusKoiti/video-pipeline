"""Constantes de checagem_local; dados fixos sem I/O."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from app.pipeline.models._checagem_local_types import Rotulo


class ChecagemLocalConstants:
    KINDS: Final = ("real", "numero", "trecho_alheio", "superlativo")
    PROMPT_FILE: Final = Path("prompts/local/checagem.md")
    _FICHA: Final = re.compile("\\s*\\(F\\d+(?:[,;]\\s*F\\d+)*\\)")
    _NUMBER: Final = re.compile("\\d[\\d.]*")
    _WORD: Final = re.compile("\\w{5,}")
    SUPERLATIVE: Final[str] = " Foi o maior de todo o país."
    EXPECTED: Final[Mapping[str, Rotulo]] = MappingProxyType(
        {"real": "SUSTENTA", "numero": "DIVERGE", "trecho_alheio": "SEM_SUPORTE", "superlativo": "EXAGERO"}
    )
