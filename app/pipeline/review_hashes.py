"""Hash do conteúdo revisado, com normalização de escolhas derivadas do roteiro."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from app.pipeline.constants.gates_constants import GatesConstants as Constants
from app.pipeline.numbers import strip_block


def content_hash(paths: list[Path], *, base: Path) -> str:
    """Como `compute_input_hash`, sem o que é derivado ou escolhido depois do roteiro: no `scenes.json`, todo
    `asset_id` conta como `null`; no `outline.md`, o bloco de números gerado (`vp numeros`) não conta. Um
    roteiro sem imagens e sem bloco tem o mesmo hash de antes."""
    return hash_contents({path: path.read_bytes() for path in paths}, base=base)


def hash_contents(contents: Mapping[Path, bytes], *, base: Path) -> str:
    """O mesmo hash, sobre o conteúdo informado: confere o que uma escrita mudaria antes de gravar."""
    digest = hashlib.sha256()
    for path in sorted(contents):
        data = contents[path]
        if path.name == "scenes.json":
            data = Constants.ASSET_ID.sub(rb"\1null", data)
        elif path.name == "outline.md":
            data = strip_block(data)  # os números gerados saem do scenes.json, já carimbado (#170)
        digest.update(path.relative_to(base).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(data).digest())
    digest.update(json.dumps({}).encode())
    return "sha256:" + digest.hexdigest()
