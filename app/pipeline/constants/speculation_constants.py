"""Constantes da especulação declarada por cena (ADR 065); dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class SpeculationConstants:
    # Marcas de especulação na fala de uma cena `especulacao`, em minúsculas e sem acento: sem nenhuma, a cena
    # soa como crônica da linha inventada, o que a análise do nicho mediu no terço de menos views.
    MARKS: Final[tuple[str, ...]] = (
        "provavelmente",
        "seria",
        "seriam",
        "teria",
        "teriam",
        "o mais provavel",
        "eu acho",
        "acho que",
        "talvez",
        "na minha leitura",
        "possivelmente",
        "poderia",
        "poderiam",
    )
    # O que a abertura diz antes da primeira cena `especulacao` para avisar que a linha muda ("as regras do
    # jogo"), também em minúsculas e sem acento.
    OPENING_MARKS: Final[tuple[str, ...]] = ("e se", "vou mudar", "a partir daqui")
    # Ano de quatro dígitos na fala da especulação: sinal de crônica ("em 1995, o Brasil…").
    _YEAR: Final = re.compile(r"(?<![\d.,])(1\d{3}|20\d{2})(?!\d|[.,]\d)")
