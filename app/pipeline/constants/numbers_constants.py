"""Constantes de numbers; dados fixos sem I/O."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Final


class NumbersConstants:
    MAX_SHOT_MS: Final[int] = 6000
    LONG_KINDS: Final = frozenset(("network", "timeline", "broll"))
    # a abertura é o primeiro décimo da duração estimada (decisão D2 da spec)
    OPENING_SHARE: Final[float] = 0.1
    # as medidas "_60s" do nicho olham o primeiro minuto
    OPENING_S: Final[int] = 60
    BLOCK_START: Final[str] = "<!-- números: gerado por `vp numeros`; não editar à mão -->"
    BLOCK_END: Final[str] = "<!-- números: fim -->"
    FORMAT_FILE: Final[str] = "formato-brief.json"
    IMAGE_PLAN_FILE: Final[str] = "plano-imagens.md"
    SPOKEN: Final = MappingProxyType(
        {
            "voce": re.compile("\\b(você|vocês)\\b", re.I),
            "nos": re.compile("\\b(a gente|nós|nosso|nossa|nossos|nossas)\\b", re.I),
            "eu": re.compile("\\b(eu|meu|minha|pra mim|para mim|acho)\\b", re.I),
            "fonte": re.compile(
                "\\b(segundo|de acordo com|estudo|estudos|pesquisa|pesquisas|pesquisadores|artigo)\\b", re.I
            ),
        }
    )
    MEASURE_LABELS: Final = MappingProxyType(
        {
            "duracao_s": "duração (s)",
            "palavras_min": "palavras por minuto",
            "cortes_min": "trocas de imagem por minuto",
            "plano_medio_s": "plano médio (s)",
            "voce_por_mil": '"você" por mil palavras',
            "nos_por_mil": '"a gente" por mil palavras',
            "eu_por_mil": '"eu" por mil palavras',
            "fonte_por_mil": "fonte citada por mil palavras",
            "palavras_60s": "palavras no primeiro minuto",
            "voce_60s": '"você" no primeiro minuto',
            "cortes_60s": "trocas de imagem no primeiro minuto",
        }
    )
