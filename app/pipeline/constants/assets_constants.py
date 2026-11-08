"""Constantes da entrada de ativos; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final


class AssetsConstants:
    # mídia de banco de imagem; a extensão do arquivo baixado sai da URL, senão do tipo do id
    MEDIA_SUFFIXES: Final = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm")
    VIDEO_MARK: Final[str] = "-video-"
    DEFAULT_VIDEO_SUFFIX: Final[str] = ".mp4"
    DEFAULT_PHOTO_SUFFIX: Final[str] = ".jpg"
    # leitura do arquivo para o sha256
    CHUNK_BYTES: Final[int] = 1 << 20
