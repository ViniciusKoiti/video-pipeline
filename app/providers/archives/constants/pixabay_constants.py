"""Constantes de pixabay; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final

from app.pipeline.models.provider import Provider


class PixabayConstants:
    API: Final[str] = "https://pixabay.com/api/"
    PER_PAGE: Final[int] = 20
    # limite da API para `q`
    MAX_QUERY_CHARS: Final[int] = 100
    LICENSE_URL: Final[str] = 'https://pixabay.com/service/license-summary/'
    LICENSE_ID: Final[str] = 'Pixabay'
    PROVIDER: Final[Provider] = Provider.PIXABAY
