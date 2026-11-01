"""Constantes de pexels; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final

from app.pipeline.models.provider import Provider


class PexelsConstants:
    API: Final[str] = "https://api.pexels.com/v1"
    # por busca; os filtros de resolução e duração descartam parte
    PER_PAGE: Final[int] = 15
    LICENSE_URL: Final[str] = 'https://www.pexels.com/license/'
    LICENSE_ID: Final[str] = 'Pexels'
    PROVIDER: Final[Provider] = Provider.PEXELS
