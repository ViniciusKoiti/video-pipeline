"""Hash do conteúdo revisado, com normalização de escolhas derivadas do roteiro."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from app.pipeline.constants.gates_constants import GatesConstants as Constants
from app.pipeline.constants.numbers_constants import NumbersConstants
from app.pipeline.governance.state import compute_input_hash


def content_hash(paths: list[Path], *, base: Path) -> str:
    """Como `compute_input_hash`, sem o que é derivado ou escolhido depois do roteiro: no `scenes.json`, as
    chaves `asset_id` não contam (com ou sem a chave, o hash é o mesmo); no `outline.md`, o bloco de números
    gerado (`vp numeros`) não conta. Um roteiro sem imagens e sem bloco tem o mesmo hash de antes."""
    return hash_contents({path: path.read_bytes() for path in paths}, base=base)


def legacy_content_hash(paths: list[Path], *, base: Path) -> str:
    """O carimbo de antes desta regra: todo `asset_id` contava como `null`, mas a chave nova mudava o hash."""
    return hash_contents({path: path.read_bytes() for path in paths}, base=base, null_asset_ids=True)


def legacy_hashes_of(paths: list[Path], *, base: Path) -> tuple[str, str]:
    """Os carimbos das regras anteriores (decisões antigas continuam valendo): o arquivo inteiro e o hash em
    que o `asset_id` contava como `null`."""
    return compute_input_hash(paths, {}, base=base), legacy_content_hash(paths, base=base)


def strip_asset_ids(data: bytes) -> bytes:
    for pattern in (Constants.ASSET_ID_AFTER, Constants.ASSET_ID_BEFORE, Constants.ASSET_ID_ALONE):
        data = pattern.sub(b"", data)
    return data


def hash_contents(contents: Mapping[Path, bytes], *, base: Path, null_asset_ids: bool = False) -> str:
    """O mesmo hash, sobre o conteúdo informado: confere o que uma escrita mudaria antes de gravar."""
    digest = hashlib.sha256()
    for path in sorted(contents):
        data = contents[path]
        if path.name == "scenes.json":
            data = Constants.ASSET_ID.sub(rb"\1null", data) if null_asset_ids else strip_asset_ids(data)
        elif path.name == "outline.md":
            data = strip_block(data)  # os números gerados saem do scenes.json, já carimbado (#170)
        digest.update(path.relative_to(base).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(data).digest())
    digest.update(json.dumps({}).encode())
    return "sha256:" + digest.hexdigest()


def strip_block(data: bytes) -> bytes:
    """Os bytes sem o bloco gerado: o carimbo do gate 2 e o do parecer não dependem dele (decisão D1).

    Sem bloco, os bytes voltam iguais. Com bloco, sai também a linha em branco que o `replace_block` põe antes
    dele: o outline aprovado antes do bloco tem o mesmo carimbo depois de ganhá-lo."""
    start_mark, end_mark = NumbersConstants.BLOCK_START.encode(), NumbersConstants.BLOCK_END.encode()
    start, end = data.find(start_mark), data.find(end_mark)
    if start < 0 or end < start:
        return data
    before, after = data[:start].rstrip(b"\n"), data[end + len(end_mark) :]
    if not after.strip():
        return before + b"\n"
    return before + b"\n\n" + after.lstrip(b"\n")
