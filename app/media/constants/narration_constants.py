"""Constantes de narration; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class NarrationConstants:
    PAUSE_TAG: Final[str] = "<short pause>"
    # reservada ao lote de cenas do Gemini (ADR 012), nunca dentro da narração
    LONG_PAUSE_TAG: Final[str] = "<long pause>"
    # ≈0,75 s a 13 caracteres por segundo; no teste de 2026-10-05 as pausas ficaram em 0,5–1,1 s
    PAUSE_CHARS: Final[int] = 10
    _PAUSE: Final = re.compile("[ \\t]*<short pause>[ \\t]*")
    _WELL_PLACED: Final = re.compile("(?<=\\S) <short pause> (?=\\S)")
    _ANY_TAG: Final = re.compile("<[^<>]*>")
    # Marcas de emoção por trecho (ADR 063): abrem e fecham em volta de uma frase ou oração, sem ocupar espaço
    # no texto falado. Lista fechada; cada voz traduz do seu jeito (o Azure, por `[azure_speech.styles]`).
    EMOTION_TAGS: Final[tuple[str, ...]] = (
        "raiva", "sussurro", "suspense", "surpresa", "tristeza",
        "esperanca", "firme", "acolhedor", "arrependimento", "empolgacao",
    )
    _EMOTION: Final = re.compile("</?(?:" + "|".join(EMOTION_TAGS) + ")>")
    _EMOTION_PARTS: Final = re.compile("<(/?)(" + "|".join(EMOTION_TAGS) + ")>")
    EMOTION_MIN_WORDS: Final[int] = 3  # menos que isso numa marca: cada corte reinicia a entonação
    EMOTION_MAX_PER_SCENE: Final[int] = 2
