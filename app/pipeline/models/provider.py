from __future__ import annotations

from enum import StrEnum


class Provider(StrEnum):
    WIKIMEDIA_COMMONS = "wikimedia_commons"
    LIBRARY_OF_CONGRESS = "library_of_congress"
    FLICKR_COMMONS = "flickr_commons"
    PEXELS = "pexels"
    PIXABAY = "pixabay"
    UNSPLASH = "unsplash"
    COVERR = "coverr"  # só clipes baixados à mão pelo site (ADR 007, emenda de bancos de imagem)
    WORKERS_AI = "workers_ai"
    ORIGINAL = "original"  # mapa, cronologia ou tela gráfica feitos pelo projeto
    OFFICIAL = "official"  # material oficial público do detentor da obra (emenda de citação, ADR 007)
    YOUTUBE_AUDIO_LIBRARY = "youtube_audio_library"  # faixa baixada à mão pelo Studio (ADR 030)
