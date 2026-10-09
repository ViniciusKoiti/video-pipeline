"""Fonte no rodapé dos planos (ADR 011, decisão 6).

O texto sai das `claims` do plano e do `sources.json`, sem campo no roteiro e sem editar o `sources.json`
(editar derrubaria a aprovação do gate 1). Quem escreve o roteiro não escolhe o que aparece como fonte.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.pipeline.schemas import Claim, Language, Source, SourcesManifest

MAX_LABELS = 2
MAX_TITLE = 60
INTERESTED_FLAG = "fonte interessada"  # pt-BR, o idioma padrão
# Palavras do rodapé por idioma (ADR 011, emenda "número por idioma"): "A e B" / "A and B", "A e outros" /
# "A et al.", "... e outras" / "... and others" e a ressalva de fonte interessada.
_WORDS: dict[Language, dict[str, str]] = {
    "pt-BR": {"and": "e", "authors": "e outros", "sources": "e outras", "interested": INTERESTED_FLAG},
    "en": {"and": "and", "authors": "et al.", "sources": "and others", "interested": "interested source"},
}


def source_label(source: Source, language: Language = "pt-BR") -> str:
    """Sobrenomes dos autores ("A", "A e B", "A e outros"; em inglês "A and B", "A et al."); sem autores, o
    título até o primeiro " — "."""
    words = _WORDS[language]
    surnames = [author.split(",")[0].strip() for author in source.authors if author.strip()]
    if len(surnames) == 1:
        return surnames[0]
    if len(surnames) == 2:
        return f"{surnames[0]} {words['and']} {surnames[1]}"
    if surnames:
        return f"{surnames[0]} {words['authors']}"
    title = source.title.split(" — ")[0].strip()
    if len(title) <= MAX_TITLE:
        return title
    cut = title[: MAX_TITLE - 1].rsplit(" ", 1)[0]
    return f"{cut}…"


def shot_attribution(
    claims: Sequence[Claim], sources: SourcesManifest, language: Language = "pt-BR"
) -> tuple[str | None, str | None]:
    """(fonte, ressalva) do rodapé de um plano. Fontes com os mesmos autores viram um rótulo só; até dois
    rótulos, e "e outras" além disso. A ressalva "fonte interessada" aparece quando todas as fontes do plano
    são interessadas: o que está na tela depende só delas."""
    by_id = {s.id: s for s in sources.sources}
    used = [by_id[i] for i in dict.fromkeys(i for c in claims for i in c.source_ids) if i in by_id]
    if not used:
        return None, None
    words = _WORDS[language]
    labels = list(dict.fromkeys(source_label(s, language) for s in used))
    text = "; ".join(labels[:MAX_LABELS])
    if len(labels) > MAX_LABELS:
        text += f" {words['sources']}"
    flag = words["interested"] if all(s.interested for s in used) else None
    return text, flag
