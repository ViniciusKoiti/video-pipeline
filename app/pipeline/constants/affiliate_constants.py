"""Constantes de affiliate; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class AffiliateConstants:
    BOOKS_FILE: Final[str] = "livros.json"
    CHANNEL_FILE: Final[str] = "config/canal.toml"
    DESCRIPTION_FILE: Final[str] = "description.txt"
    AMAZON_HOSTS: Final = ("amazon.com.br", "www.amazon.com.br", "amzn.to")
    DISCLOSURE: Final[str] = (
        "Como participante do Programa de Associados da Amazon, sou remunerado "
        "pelas compras qualificadas efetuadas."
    )
    BLOCK_START: Final[str] = "📚 Livros citados no vídeo:"
    BLOCK_END: Final = DISCLOSURE
