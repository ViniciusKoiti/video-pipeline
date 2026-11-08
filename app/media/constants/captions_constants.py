"""Constantes de captions; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class CaptionsConstants:
    CAPTIONS: Final[str] = "captions.srt"
    OLD_CAPTIONS: Final[str] = "captions.old.srt"
    KEY: Final[str] = "captions.key"
    # muda quando a divisão ou o tempo mudam: a legenda gerada antes é refeita
    VERSION: Final[int] = 1
    # duas linhas da legenda em retrato (54 px em 86% de 1080 cabem ~31 caracteres por linha)
    MAX_CHARS: Final[int] = 60
    # bloco mais curto que isto não dá tempo de ler
    MIN_CUE_MS: Final[int] = 600
    # distância máxima entre a posição proporcional e o silêncio onde a fronteira cai
    SNAP_MS: Final[int] = 600
    # numa marca `<short pause>` o silêncio existe com certeza: procura mais longe
    PAUSE_SNAP_MS: Final[int] = 1500
    # arredondamento tolerado no fim do áudio
    END_SLACK_MS: Final[int] = 40
    _SENTENCE: Final = re.compile("(?<=[.!?;:])\\s+")
    _COMMA: Final = re.compile("(?<=,)\\s+")
    _SRT_TIME: Final = re.compile("(\\d{2}):(\\d{2}):(\\d{2}),(\\d{3})")
    _WORD: Final = re.compile("[\\wÀ-ÿ]+(?:-[\\wÀ-ÿ]+)*")
    _NUMBER_WORDS: Final = frozenset(
        (
            "dois",
            "duas",
            "três",
            "quatro",
            "cinco",
            "seis",
            "sete",
            "oito",
            "nove",
            "dez",
            "onze",
            "doze",
            "treze",
            "catorze",
            "quatorze",
            "quinze",
            "dezesseis",
            "dezessete",
            "dezoito",
            "dezenove",
            "vinte",
            "trinta",
            "quarenta",
            "cinquenta",
            "sessenta",
            "setenta",
            "oitenta",
            "noventa",
            "cem",
            "cento",
            "duzentos",
            "trezentos",
            "quatrocentos",
            "quinhentos",
            "seiscentos",
            "setecentos",
            "oitocentos",
            "novecentos",
            "mil",
            "milhão",
            "milhões",
            "bilhão",
            "bilhões",
            "real",
            "reais",
            "centavo",
            "centavos",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "twenty",
            "thirty",
            "forty",
            "fifty",
            "sixty",
            "seventy",
            "eighty",
            "ninety",
            "hundred",
            "thousand",
            "million",
            "billion",
        )
    )
