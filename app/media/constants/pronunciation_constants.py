"""Constantes de pronunciation; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class PronunciationConstants:
    GLOSSARY_FILE: Final[str] = "voice/glossary.json"
    # alfabeto do campo `ipa` do glossário: a voz que o declara (`PhonemeTTS`) lê o termo pelos fonemas
    IPA: Final[str] = "ipa"
