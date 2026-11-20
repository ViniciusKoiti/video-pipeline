"""Bytes de imagem recebidos de um gerador: tipo pelo começo do arquivo e gravação inteira."""

from __future__ import annotations

import os
from pathlib import Path

from app.providers.errors import InvalidOutput
from app.providers.image_gen.constants.browser_constants import BrowserConstants


def extension(provider: str, data: bytes) -> str:
    """Extensão pelo começo do arquivo; o que não é PNG, JPEG ou WebP não é imagem aceita."""
    for start, suffix in BrowserConstants.SIGNATURES:
        if data.startswith(start):
            return suffix
    raise InvalidOutput(provider, "o que o site devolveu não é PNG, JPEG nem WebP")


def write_image(provider: str, out_path: Path, data: bytes) -> Path:
    """Grava em `out_path` com a extensão dos bytes, por temporário + rename: nunca um arquivo pela metade."""
    target = out_path.with_suffix(extension(provider, data))
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, target)
    return target
