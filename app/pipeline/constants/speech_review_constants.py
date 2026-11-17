"""Constantes de speech_review; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class SpeechReviewConstants:
    REPORT_FILE: Final[str] = "voice/conferencia.json"
    SHEET_FILE: Final[str] = "voice/conferencia-escuta.wav"
    # palavra comum mais curta que isso, trocada pelo reconhecedor, é ruído dele (artigo, preposição)
    MIN_CONTENT_LETTERS: Final[int] = 4
    # o termo ouvido parecido com a grafia ou com a `fala` do glossário pelo menos isso passa
    TERM_SIMILARITY: Final[float] = 0.75
    # na folha de escuta: quanto antes e depois de cada trecho, e o silêncio entre eles
    CLIP_PAD_MS: Final[int] = 700
    GAP_MS: Final[int] = 900
