"""`vp check`: valida o que agentes ou pessoas escreveram, sem chamar modelo nenhum (ADR 009).

Confere, no que existir na pasta do episódio: `sources.json` e os textos extraídos; `facts.json` (cada
citação é literal e está no trecho citado; fontes independentes); `scenes.json` (schema, âncoras, fontes
e trechos das afirmações, uso só de fatos fichados, ritmo estimado pela narração). Erro bloqueia o gate;
alerta vai para a revisão humana.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import ValidationError

from app.pipeline.excerpts import excerpts_of, quote_in_excerpt
from app.pipeline.ports import M, ManifestStore
from app.pipeline.schemas import (
    FactKind,
    FactsManifest,
    ScenesManifest,
    SourcesManifest,
    effective_shots,
    unknown_source_refs,
)
from app.pipeline.shots import MIN_SHOT_MS, shot_bounds

# Ritmo de fala medido no exemplo com pm_alex (150 caracteres em 9,95 s). Só estimativa: o tempo real
# vem do WAV (§9).
CHARS_PER_SECOND = 15.0
MAX_SHOT_MS = 6000


@dataclass
class CheckReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _read(
    store: ManifestStore, episode_id: str, name: str, model: type[M], report: CheckReport
) -> M | None:
    if not store.exists(episode_id, name):
        return None
    try:
        return store.read(episode_id, name, model)
    except ValidationError as error:
        problems = "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in error.errors()[:5]
        )
        report.errors.append(f"{name}: {problems}")
        return None


def _check_sources(
    store: ManifestStore, episode_id: str, sources: SourcesManifest, report: CheckReport
) -> dict[str, str]:
    excerpts: dict[str, str] = {}
    for source in sources.sources:
        path = store.path(episode_id, source.local_path)
        if not path.is_file():
            report.errors.append(f"sources.json: texto de {source.id} ausente em {source.local_path}")
            continue
        excerpts |= excerpts_of(source, path.read_text(encoding="utf-8"))
    report.checked.append(f"sources.json: {len(sources.sources)} fonte(s), {len(excerpts)} trecho(s)")
    return excerpts


def _check_facts(
    facts: FactsManifest, sources: SourcesManifest, excerpts: dict[str, str], report: CheckReport
) -> None:
    interested = {s.id for s in sources.sources if s.interested}
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
            report.warnings.append(f"{fact.id}: uma fonte só ({fact.source_ids[0]})")
    kinds = {kind: sum(f.kind is kind for f in facts.facts) for kind in FactKind}
    summary = ", ".join(f"{kind.value} {count}" for kind, count in kinds.items() if count)
    report.checked.append(f"facts.json: {len(facts.facts)} fato(s) ({summary})")
    if kinds[FactKind.CONTEXT] == len(facts.facts):
        report.warnings.append("facts.json: só contexto; falta o que prenda (número, conflito, virada...)")


def _check_scenes(
    scenes: ScenesManifest,
    sources: SourcesManifest | None,
    facts: FactsManifest | None,
    excerpts: dict[str, str],
    report: CheckReport,
) -> None:
    if sources is not None:
        report.errors += unknown_source_refs(scenes, sources)
    fact_excerpts = {e.excerpt_id for f in facts.facts for e in f.evidence} if facts else set()
    total_ms, shots = 0.0, 0
    for scene in scenes.scenes:
        claims = scene.claims + [c for shot in scene.shots for c in shot.claims]
        for claim in claims:
            if facts is not None and not claim.excerpt_ids:
                report.errors.append(f"{scene.id}: afirmação sem trecho: {claim.text!r}")
            for excerpt_id in claim.excerpt_ids:
                if sources is not None and excerpt_id not in excerpts:
                    report.errors.append(f"{scene.id}: trecho {excerpt_id} não existe")
                elif facts is not None and excerpt_id not in fact_excerpts:
                    report.errors.append(f"{scene.id}: trecho {excerpt_id} não está em nenhuma ficha")
        duration_ms = len(scene.narration) / CHARS_PER_SECOND * 1000
        total_ms += duration_ms
        planned = effective_shots(scene)
        shots += len(planned)
        try:
            bounds = shot_bounds(scene.narration, planned, round(duration_ms))
        except ValueError as error:
            report.errors.append(f"{scene.id}: {error}")
            continue
        for shot, (_, ms) in zip(planned, bounds, strict=True):
            if not MIN_SHOT_MS <= ms <= MAX_SHOT_MS:
                report.warnings.append(
                    f"{scene.id}: plano {shot.kind} ({shot.anchor!r}) com ~{ms / 1000:.1f} s"
                )
    report.checked.append(
        f"scenes.json: {len(scenes.scenes)} cena(s), {shots} plano(s), ~{total_ms / 1000:.0f} s de narração "
        f"(média ~{total_ms / shots / 1000:.1f} s por plano, estimada)"
    )


def check_episode(store: ManifestStore, episode_id: str) -> CheckReport:
    report = CheckReport()
    sources = _read(store, episode_id, "sources.json", SourcesManifest, report)
    facts = _read(store, episode_id, "facts.json", FactsManifest, report)
    scenes = _read(store, episode_id, "scenes.json", ScenesManifest, report)
    excerpts = _check_sources(store, episode_id, sources, report) if sources else {}
    if facts is not None:
        if sources is None:
            report.errors.append("facts.json sem sources.json: fato só a partir de fonte baixada (§2.2)")
        else:
            _check_facts(facts, sources, excerpts, report)
    if scenes is not None:
        _check_scenes(scenes, sources, facts, excerpts, report)
    if not report.checked and not report.errors:
        report.errors.append(f"nada para validar em {episode_id} (sources.json, facts.json, scenes.json)")
    return report
