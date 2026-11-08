"""Hash de um arquivo de mídia, lido em blocos (os vídeos passam de dezenas de MB)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from app.pipeline.constants.assets_constants import AssetsConstants


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(AssetsConstants.CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()
