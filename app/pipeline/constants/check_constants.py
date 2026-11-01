"""Constantes de check; dados fixos sem I/O."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final


class CheckConstants:
    CHARS_PER_SECOND: Final[float] = 15.0
    # planos gráficos seguidos sem foto nem B-roll na tela
    MAX_GRAPHIC_RUN: Final[int] = 4
    MAX_STAMP_SHARE: Final[float] = 0.1
    # porcentagem de poucos planos não diz nada
    MIN_SHOTS_FOR_SHARE: Final[int] = 10
    # tempo mínimo de leitura de gráfico, comparação, rede, cronologia e documento
    READING_MS: Final[int] = 4000
    READING_KINDS: Final = frozenset(("chart", "compare", "network", "timeline", "calculation", "receipt"))
    BAR_TYPES: Final = frozenset(("bar", "bar_horizontal"))
    BAR_PLAIN_BELOW: Final[int] = 1000
    # depois disso o fato não é mais notícia: o vídeo explica ou opina (ADR 019)
    NEWS_MAX_AGE_DAYS: Final[int] = 30
    FUNNEL_ASKS: Final[Mapping[str, tuple[str, tuple[str, ...]]]] = MappingProxyType(
        {
            "topo": ("seguir ou compartilhar", ("segu", "compartilh", "manda", "envia")),
            "meio": ("salvar ou comentar", ("salv", "coment")),
            "fundo": ("pedir o que é oferecido", ("coment", "link", "bio", "direct", "ped", "baix", "chama")),
        }
    )
    END_CARD_VARIANTS: Final = MappingProxyType({"topo": "follow", "meio": "save"})
