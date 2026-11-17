"""Constantes de funnel_check; dados fixos sem I/O."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final


class FunnelCheckConstants:
    # O que a chamada de cada estágio pede (ADR 026 e emenda de 2026-11-16), como começo de palavra sem
    # acento: "salva", "salvar" e "salve" valem para "salv". Uma entrada com espaço pede palavras seguidas:
    # "proxim episod" vale para "próximo episódio". Chamada sem nenhuma delas pede outra coisa: erro.
    FUNNEL_ASKS: Final[Mapping[str, tuple[str, tuple[str, ...]]]] = MappingProxyType(
        {
            "topo": (
                "seguir, se inscrever, ver o próximo vídeo ou compartilhar",
                ("segu", "inscrev", "compartilh", "manda", "envia", "proxim vide", "proxim episod"),
            ),
            "meio": (
                "salvar, comentar ou ver o próximo vídeo",
                ("salv", "coment", "proxim vide", "proxim episod"),
            ),
            "fundo": ("pedir o que é oferecido", ("coment", "link", "bio", "direct", "ped", "baix", "chama")),
        }
    )
    # A variante do cartão final por estágio (ADR 028); `next` vale em qualquer um, quando a série continua. O
    # fundo ainda não tem variante: o contrato recusa o cartão final nele.
    END_CARD_VARIANTS: Final = MappingProxyType({"topo": "follow", "meio": "save"})
    # Daqui para cima o vídeo é longo e o fecho leva a pergunta dos comentários antes da chamada (os Shorts
    # ficam com um pedido só, ADR 028).
    LONG_VIDEO_SECONDS: Final[float] = 180.0
    # A chamada que já pede comentário dispensa a pergunta separada.
    COMMENT_PREFIX: Final[str] = "coment"
