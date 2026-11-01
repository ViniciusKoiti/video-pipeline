from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedSource:
    """O original e o texto tirado dele, prontos para registrar; nada foi escrito ainda."""

    raw: bytes
    suffix: str  # extensão do original em `sources/raw/`: "html", "pdf", "md", "txt"
    paragraphs: tuple[str, ...]  # um parágrafo = um trecho numerado (ADR 009)
