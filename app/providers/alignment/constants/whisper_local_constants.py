"""Constantes de whisper_local; dados fixos sem I/O."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final


class WhisperLocalConstants:
    # o idioma do episódio no nome que o Whisper do transformers aceita
    LANGUAGES: Final = MappingProxyType({"pt": "portuguese", "en": "english"})
    TASK: Final[str] = "automatic-speech-recognition"
    DOWNLOAD_HINT: Final[str] = "baixe uma vez com `uv run hf download {model}` (~1 GB, apache-2.0)"
