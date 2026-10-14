"""Trechos numerados das fontes (CLAUDE.md §13.1, ADR 009).

O texto extraído de cada fonte (`Source.local_path`) é dividido em parágrafos, separados por linha em
branco; o n-ésimo parágrafo é o trecho `<source-id>#E<n>`. A numeração é determinística: quem escreve
fichas e roteiro (agente, modelo local ou pessoa) cita o trecho, e o código confere a citação.
"""

from __future__ import annotations

import re

from app.pipeline.schemas import Source

_BLANK_LINE = re.compile(r"\n\s*\n")
_ELISION = re.compile(r"\s*(?:\[\.\.\.\]|\[…\]|\.\.\.|…)\s*")
_TYPOGRAPHY = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-", " ": " "})


def _normalize(text: str) -> str:
    return " ".join(text.translate(_TYPOGRAPHY).split())


def split_excerpts(text: str) -> list[str]:
    """Parágrafos do texto, com espaços normalizados; o índice 0 é o trecho E1."""
    return [" ".join(block.split()) for block in _BLANK_LINE.split(text) if block.strip()]


def excerpts_of(source: Source, text: str) -> dict[str, str]:
    return {f"{source.id}#E{i}": paragraph for i, paragraph in enumerate(split_excerpts(text), start=1)}


def quote_in_excerpt(quote: str, excerpt: str) -> bool:
    """A citação é cópia literal do trecho; "..." ou "[...]" marcam cortes, e as partes vêm em ordem.
    Aspas curvas, travessões e espaços não contam como diferença."""
    haystack, cursor = _normalize(excerpt), 0
    for part in _ELISION.split(quote):
        part = _normalize(part)
        if not part:
            continue
        found = haystack.find(part, cursor)
        if found < 0:
            return False
        cursor = found + len(part)
    return cursor > 0


def numbered_view(source: Source, text: str) -> str:
    """Texto da fonte com o id de cada trecho, para ler e citar (`vp excerpts`)."""
    origin = source.url or "Fonte declarada pelo dono, sem URL: ele responde por ela."
    header = f"# {source.id} — {source.title}\n\n{origin}\n"
    if source.interested:
        header += "\nFonte interessada: nenhum fato só com ela.\n"
    numbered = excerpts_of(source, text).items()
    body = "\n\n".join(f"[{excerpt_id}] {paragraph}" for excerpt_id, paragraph in numbered)
    return f"{header}\n{body}\n"
