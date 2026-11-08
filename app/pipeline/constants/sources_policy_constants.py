"""Constantes do regime de fontes de um roteiro (ADR 056); dados fixos sem I/O."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final


class SourcesPolicyConstants:
    DEFAULT: Final[str] = "documental"
    # regimes em que número, data, citação, cargo ou gráfico na tela exige claim (ADR 008)
    CLAIMS_ON_SCREEN: Final[frozenset[str]] = frozenset({"documental", "ensaio"})
    # regimes em que a fonte aparece no rodapé do plano (ADR 011); nos outros, só na descrição
    FOOTER: Final[frozenset[str]] = frozenset({"documental"})
    # o que cada regime promete, para o `vp check` e o `vp status`
    DESCRIPTIONS: Final[Mapping[str, str]] = MappingProxyType(
        {
            "documental": "fichas e claims obrigatórias; fonte no rodapé e na descrição",
            "ensaio": "fichas obrigatórias; claim no que vai à tela; fonte só na descrição",
            "entretenimento": "sem fichas nem claims; fato sobre pessoa viva ou empresa ativa segue exigindo",
        }
    )
