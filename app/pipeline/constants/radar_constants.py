"""Constantes de radar; dados fixos sem I/O."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Final


class RadarConstants:
    MEASURES: Final = MappingProxyType(
        {
            "shares/views": "compartilhamentos por visualização",
            "likes/views": "curtidas por visualização",
            "comments/views": "comentários por visualização",
        }
    )
    BRIEF_FILE: Final[str] = "radar-brief.json"
    CAPTION_FILE: Final[str] = "legenda-post.txt"
    # depois disso o resumo descreve Reels que já saíram de circulação
    MAX_AGE_DAYS: Final[int] = 45
    # o título de alerta conta se for um dos primeiros planos da primeira cena
    OPENING_SHOTS: Final[int] = 2
    # abaixo disso o resumo leu poucos Reels e os padrões ficam como hipótese (skill `pauta`)
    MIN_ANALYSED: Final[int] = 30
    _VIEWER: Final = MappingProxyType(
        {
            "pt-BR": "\\b(você|vocês|seu|sua|seus|suas|teu|tua|teus|tuas|contigo)\\b",
            "en": "\\b(you|your|yours)\\b",
        }
    )
    _SENTENCE_END: Final = re.compile("(?<=[.?!…])\\s+")
    _EMOJI: Final = re.compile("[🀀-\U0001faff☀-➿⬀-⯿]")
    _ASKS_COMMENT: Final = re.compile("coment|comment", re.IGNORECASE)
    PURPOSE_KINDS: Final = MappingProxyType(
        {"purpose_news": "noticiar", "purpose_explain": "explicar", "purpose_opinion": "opinar"}
    )
