"""Constantes de short_speech; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class ShortSpeechConstants:
    # Uma conferência por narração: a mesma pasta pode ter a versão pt e a en (`narracao.pt.json`,
    # `narracao.en.json`).
    REPORT_FILE: Final[str] = "voice/conferencia-{stem}.json"
    SHEET_FILE: Final[str] = "voice/conferencia-{stem}-escuta.wav"
    RECORD_SUFFIX: Final[str] = ".voz.json"  # o registro que `vp short voz` escreve ao lado da narração
