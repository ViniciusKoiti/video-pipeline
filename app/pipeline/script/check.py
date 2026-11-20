"""`vp check`: valida o que agentes ou pessoas escreveram, sem chamar modelo nenhum (ADR 009).

Confere, no que existir na pasta do episódio: `sources.json` e os textos extraídos; `facts.json` (cada
citação é literal e está no trecho citado; fontes independentes); `scenes.json` (schema, âncoras, fontes
e trechos das afirmações, uso só de fatos fichados, ritmo estimado pela narração). Erro bloqueia o gate;
alerta vai para a revisão humana.

Aqui ficam a leitura dos arquivos e a execução das regras (ADR 064); cada regra mora no seu módulo em
`checks/`, e a ordem está em `checks/registry.py` (episódio) e `checks/scenes.py` (cena e plano).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path

from app.pipeline.constants.check_constants import CheckConstants as Constants
from app.pipeline.models.check_report import CheckReport as CheckReport
from app.pipeline.ports import ManifestStore
from app.pipeline.research.excerpts import excerpts_of
from app.pipeline.schemas import FactsManifest, MusicCatalog, ScenesManifest, SourceKind, SourcesManifest
from app.pipeline.script.checks.registry import EPISODE_RULES
from app.pipeline.script.models.checked_episode import CheckedEpisode
from app.pipeline.script.reading import read_optional


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
        if source.kind is SourceKind.DECLARED:
            report.warnings.append(
                f"{source.id}: fonte declarada pelo dono, sem URL; ele responde por ela no gate 1"
            )
    report.checked.append(f"sources.json: {len(sources.sources)} fonte(s), {len(excerpts)} trecho(s)")
    return excerpts


def check_episode(
    store: ManifestStore,
    episode_id: str,
    region_codes: frozenset[str] | None = None,
    chars_per_second: float = Constants.CHARS_PER_SECOND,
    today: date | None = None,
    music_catalog: MusicCatalog | None = None,
    measure: Callable[[Path], float] | None = None,
    final_voice: str | None = None,
) -> CheckReport:
    """`region_codes`: códigos de país e estado que o template sabe desenhar (sem eles, não confere).
    `chars_per_second`: ritmo da voz configurada, para estimar a duração das cenas e dos planos.
    `today`: a data de hoje: diz se o resumo do radar está velho e se o fato noticiado ainda é notícia.
    `music_catalog`: as faixas que o plano da trilha pode usar (ADR 030).
    `measure`: segundos de um WAV; com ele, o relógio de retenção usa a voz real, quando existe (ADR 061).
    `final_voice`: a voz do vídeo final; no Azure, o glossário precisa de `ipa` (CLAUDE.md §6)."""
    report = CheckReport()
    sources = read_optional(store, episode_id, "sources.json", SourcesManifest, report)
    facts = read_optional(store, episode_id, "facts.json", FactsManifest, report)
    scenes = read_optional(store, episode_id, "scenes.json", ScenesManifest, report)
    excerpts = _check_sources(store, episode_id, sources, report) if sources else {}
    episode = CheckedEpisode(
        store=store,
        episode_id=episode_id,
        sources=sources,
        facts=facts,
        scenes=scenes,
        excerpts=excerpts,
        region_codes=region_codes,
        chars_per_second=chars_per_second,
        today=today,
        music_catalog=music_catalog,
        measure=measure,
        final_voice=final_voice,
    )
    for rule in EPISODE_RULES:
        rule(episode, report)
    if not report.checked and not report.errors:
        report.errors.append(f"nada para validar em {episode_id} (sources.json, facts.json, scenes.json)")
    return report
