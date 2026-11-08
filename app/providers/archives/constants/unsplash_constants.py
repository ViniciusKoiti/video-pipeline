"""Constantes de unsplash; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final

from app.pipeline.models.provider import Provider


class UnsplashConstants:
    API: Final[str] = "https://api.unsplash.com"
    PER_PAGE: Final[int] = 20
    LICENSE_URL: Final[str] = 'https://unsplash.com/license'
    LICENSE_ID: Final[str] = 'Unsplash'
    PROVIDER: Final[Provider] = Provider.UNSPLASH
