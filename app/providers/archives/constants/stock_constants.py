"""Constantes de stock; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class StockConstants:
    IMAGE_SUFFIXES: Final = (".jpg", ".jpeg", ".png", ".webp")
    # O Unsplash responde 403 (não 429) com este corpo quando a cota horária acaba;
    # sem ele, 403 continua sendo chave recusada.
    RATE_LIMIT_BODY: Final = "rate limit exceeded"
