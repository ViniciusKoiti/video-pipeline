"""Constantes de attribution; dados fixos sem I/O."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from app.pipeline.schemas import Language


class AttributionConstants:
    MAX_LABELS: Final[int] = 2
    MAX_TITLE: Final[int] = 60
    # pt-BR, o idioma padrão
    INTERESTED_FLAG: Final[str] = "fonte interessada"
    _WORDS: Final[Mapping[Language, Mapping[str, str]]] = MappingProxyType(
        {
            "pt-BR": MappingProxyType(
                {"and": "e", "authors": "e outros", "sources": "e outras", "interested": INTERESTED_FLAG}
            ),
            "en": MappingProxyType(
                {
                    "and": "and",
                    "authors": "et al.",
                    "sources": "and others",
                    "interested": "interested source",
                }
            ),
        }
    )
