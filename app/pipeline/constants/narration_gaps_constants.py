"""Constantes de narration_gaps; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class NarrationGapsConstants:
    # o narrador dizendo que não achou, no texto sem acento e em minúsculas (pt-BR e inglês)
    PHRASES: Final = (
        r"\bnao (?:encontrei|achei|descobri|localizei|sei)\b",
        r"\bnao consegui (?:encontrar|achar|descobrir|confirmar|apurar)\b",
        r"\bi (?:couldn['’]t|could not|didn['’]t|did not|can['’]t|cannot) find\b",
        r"\bi (?:don['’]t|do not) know\b",
    )
