"""Fichas (`facts.json`): cada citação é literal e está no trecho citado; fontes independentes (ADR 009)."""

from __future__ import annotations

from collections.abc import Mapping

from app.pipeline.models.check_report import CheckReport
from app.pipeline.research.excerpts import quote_in_excerpt
from app.pipeline.schemas import FactKind, FactsManifest, SourcesManifest
from app.pipeline.script.models.checked_episode import CheckedEpisode


def independence_groups(sources: SourcesManifest) -> dict[str, str]:
    """Fonte -> grupo: fontes que compartilham um autor (mesmo por outra fonte) formam um grupo só."""
    group = {s.id: s.id for s in sources.sources}

    def root(source_id: str) -> str:
        while group[source_id] != source_id:
            source_id = group[source_id]
        return source_id

    by_author: dict[str, str] = {}
    for source in sources.sources:
        for author in source.authors:
            key = " ".join(author.casefold().split())
            if key in by_author:
                group[root(source.id)] = root(by_author[key])
            else:
                by_author[key] = source.id
    return {source_id: root(source_id) for source_id in group}


def _check_facts(
    facts: FactsManifest, sources: SourcesManifest, excerpts: Mapping[str, str], report: CheckReport
) -> None:
    interested = {s.id for s in sources.sources if s.interested}
    groups = independence_groups(sources)
    single: list[str] = []  # uma linha só para todas: eram dezenas de alertas iguais (vazio-de-ter-tudo)
    for fact in facts.facts:
        for evidence in fact.evidence:
            excerpt = excerpts.get(evidence.excerpt_id)
            if excerpt is None:
                report.errors.append(f"{fact.id}: trecho {evidence.excerpt_id} não existe")
            elif not quote_in_excerpt(evidence.quote, excerpt):
                report.errors.append(
                    f"{fact.id}: citação não está em {evidence.excerpt_id}: {evidence.quote!r}"
                )
        independent = [s for s in fact.source_ids if s not in interested]
        if not independent:
            report.warnings.append(f"{fact.id}: só fontes interessadas ({', '.join(fact.source_ids)})")
        elif len(fact.source_ids) < 2:
            single.append(f"{fact.id} ({fact.source_ids[0]})")
        elif len({groups[s] for s in independent}) < 2 and len(independent) > 1:
            report.warnings.append(f"{fact.id}: fontes com os mesmos autores ({', '.join(independent)})")
    if single:
        report.warnings.append(f"uma fonte só: {', '.join(single)}")
    kinds = {kind: sum(f.kind is kind for f in facts.facts) for kind in FactKind}
    summary = ", ".join(f"{kind.value} {count}" for kind, count in kinds.items() if count)
    report.checked.append(f"facts.json: {len(facts.facts)} fato(s) ({summary})")
    if kinds[FactKind.CONTEXT] == len(facts.facts):
        report.warnings.append("facts.json: só contexto; falta o que prenda (número, conflito, virada...)")


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.facts is None:
        return
    if episode.sources is None:
        report.errors.append("facts.json sem sources.json: fato só a partir de fonte baixada (§2.2)")
        return
    _check_facts(episode.facts, episode.sources, episode.excerpts, report)
