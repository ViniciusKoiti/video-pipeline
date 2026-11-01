"""Constantes de excerpts; dados fixos sem I/O."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Final


class ExcerptsConstants:
    _BLANK_LINE: Final = re.compile("\\n\\s*\\n")
    _ELISION: Final = re.compile("\\s*(?:\\[\\.\\.\\.\\]|\\[…\\]|\\.\\.\\.|…)\\s*")
    _TYPOGRAPHY: Final = MappingProxyType(
        str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-", "\xa0": " "})
    )
