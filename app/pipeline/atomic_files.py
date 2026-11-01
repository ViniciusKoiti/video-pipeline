"""Escrita de um arquivo inteiro ou nenhuma: temporário ao lado do destino e `replace` (RF5, G02)."""

from __future__ import annotations

from pathlib import Path


def write_atomic(path: Path, data: bytes) -> None:
    """Grava `data` em `path` sem deixar o arquivo pela metade; o temporário não sobra em caso de erro.
    Um `replace` por arquivo: vários arquivos em sequência não formam uma transação."""
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f".{path.name}.partial")
    try:
        partial.write_bytes(data)
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)
