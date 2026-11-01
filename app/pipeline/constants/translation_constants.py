"""Constantes de translation; dados fixos sem I/O."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Final


class TranslationConstants:
    NARRATION_FILE: Final[str] = "narracao.json"
    LINK_FILE: Final[str] = "traducao.json"
    # o vídeo por JSON do motion-video, quando o episódio tem
    CONTENT_FILE: Final[str] = "content.json"
    _PT_VALUES: Final = MappingProxyType(
        {
            "zero": 0,
            "dois": 2,
            "duas": 2,
            "três": 3,
            "tres": 3,
            "quatro": 4,
            "cinco": 5,
            "seis": 6,
            "sete": 7,
            "oito": 8,
            "nove": 9,
            "dez": 10,
            "onze": 11,
            "doze": 12,
            "treze": 13,
            "catorze": 14,
            "quatorze": 14,
            "quinze": 15,
            "dezesseis": 16,
            "dezessete": 17,
            "dezoito": 18,
            "dezenove": 19,
            "vinte": 20,
            "trinta": 30,
            "quarenta": 40,
            "cinquenta": 50,
            "sessenta": 60,
            "setenta": 70,
            "oitenta": 80,
            "noventa": 90,
            "cem": 100,
            "cento": 100,
            "duzentos": 200,
            "trezentos": 300,
            "quatrocentos": 400,
            "quinhentos": 500,
            "seiscentos": 600,
            "setecentos": 700,
            "oitocentos": 800,
            "novecentos": 900,
        }
    )
    _PT_SCALES: Final = MappingProxyType(
        {"mil": 1000, "milhão": 1000000, "milhões": 1000000, "bilhão": 10**9, "bilhões": 10**9}
    )
    _EN_VALUES: Final = MappingProxyType(
        {
            "zero": 0,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "eleven": 11,
            "twelve": 12,
            "thirteen": 13,
            "fourteen": 14,
            "fifteen": 15,
            "sixteen": 16,
            "seventeen": 17,
            "eighteen": 18,
            "nineteen": 19,
            "twenty": 20,
            "thirty": 30,
            "forty": 40,
            "fifty": 50,
            "sixty": 60,
            "seventy": 70,
            "eighty": 80,
            "ninety": 90,
        }
    )
    _EN_SCALES: Final = MappingProxyType({"thousand": 1000, "million": 1000000, "billion": 10**9})
    _EN_HUNDRED: Final[str] = "hundred"
    # a pontuação separa um número do outro
    _WORD: Final = re.compile("\\d+(?:[.,]\\d+)*|[^\\W\\d_]+|[,;:.!?]", re.UNICODE)
    _LEXICONS: Final = MappingProxyType(
        {
            "pt": (_PT_VALUES, _PT_SCALES, frozenset(("e",)), frozenset(("cem", "cento"))),
            "en": (_EN_VALUES, _EN_SCALES, frozenset(("and",)), frozenset()),
        }
    )
