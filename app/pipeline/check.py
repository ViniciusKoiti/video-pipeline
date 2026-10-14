"""`vp check`: valida o que agentes ou pessoas escreveram, sem chamar modelo nenhum (ADR 009).

Confere, no que existir na pasta do episódio: `sources.json` e os textos extraídos; `facts.json` (cada
citação é literal e está no trecho citado; fontes independentes); `scenes.json` (schema, âncoras, fontes
e trechos das afirmações, uso só de fatos fichados, ritmo estimado pela narração). Erro bloqueia o gate;
alerta vai para a revisão humana.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from pydantic import ValidationError

from app.media.narration import timeline_length
from app.pipeline.excerpts import excerpts_of, quote_in_excerpt
from app.pipeline.ports import M, ManifestStore
from app.pipeline.radar import (
    BRIEF_FILE,
    CAPTION_FILE,
    RadarBrief,
    brief_summary,
    form_warnings,
    unmeasured_patterns,
)
from app.pipeline.schemas import (
    MEDIA_SHOT_KINDS,
    OVERLAY_SHOT_KINDS,
    ChartShot,
    CompareShot,
    FactKind,
    FactsManifest,
    Language,
    MapShot,
    NumberShot,
    QuoteShot,
    Scene,
    ScenesManifest,
    Shot,
    SourceKind,
    SourcesManifest,
    effective_shots,
    number_format_problem,
    unknown_source_refs,
)
from app.pipeline.shots import MIN_SHOT_MS, shot_bounds
from app.pipeline.text_fit import text_fit_warnings

# Ritmo de fala padrão, medido no exemplo com pm_alex (150 caracteres em 9,95 s); a CLI passa o da voz
# configurada. Só estimativa: o tempo real vem do WAV (§9).
CHARS_PER_SECOND = 15.0
MAX_SHOT_MS = 6000
# Alertas de variedade (ADR 011, decisão 9): a revisão humana decide.
MAX_GRAPHIC_RUN = 4  # planos gráficos seguidos sem foto nem B-roll na tela
MAX_STAMP_SHARE = 0.10
MIN_SHOTS_FOR_SHARE = 10  # porcentagem de poucos planos não diz nada
READING_MS = 4000  # tempo mínimo de leitura de gráfico, comparação, rede, cronologia e documento
READING_KINDS = frozenset({"chart", "compare", "network", "timeline"})
LONG_KINDS = frozenset({"network", "timeline"})  # a câmera percorre o plano: sem teto de duração
# O BarChart do motion-kit fixado formata os valores em pt-BR (sem prop `locale`): em inglês só serve onde as
# duas convenções coincidem, que é inteiro abaixo de mil. Retirar quando o kit ganhar a prop e o pin subir.
BAR_TYPES = frozenset({"bar", "bar_horizontal"})
BAR_PLAIN_BELOW = 1000


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
        if source.kind is SourceKind.DECLARED:
            report.warnings.append(
                f"{source.id}: fonte declarada pelo dono, sem URL; ele responde por ela no gate 1"
            )
    report.checked.append(f"sources.json: {len(sources.sources)} fonte(s), {len(excerpts)} trecho(s)")
    return excerpts


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
    facts: FactsManifest, sources: SourcesManifest, excerpts: dict[str, str], report: CheckReport
) -> None:
    interested = {s.id for s in sources.sources if s.interested}
    groups = independence_groups(sources)
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
        elif len({groups[s] for s in independent}) < 2 and len(independent) > 1:
            report.warnings.append(f"{fact.id}: fontes com os mesmos autores ({', '.join(independent)})")
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
    region_codes: frozenset[str] | None = None,
    chars_per_second: float = CHARS_PER_SECOND,
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
        duration_ms = timeline_length(scene.narration) / chars_per_second * 1000
        total_ms += duration_ms
        planned = effective_shots(scene)
        shots += len(planned)
        try:
            bounds = shot_bounds(scene.narration, planned, round(duration_ms))
        except ValueError as error:
            report.errors.append(f"{scene.id}: {error}")
            continue
        media_before = False  # foto ou B-roll da cena já na tela: tarja, número e carimbo vão por cima
        for shot, (_, ms) in zip(planned, bounds, strict=True):
            report.warnings += text_fit_warnings(
                scene.id, shot, ms, media_before and shot.kind in OVERLAY_SHOT_KINDS
            )
            report.errors += number_errors(scene.id, shot, scenes.language)
            media_before = media_before or shot.kind in MEDIA_SHOT_KINDS
            too_long = ms > MAX_SHOT_MS and shot.kind not in LONG_KINDS
            if ms < MIN_SHOT_MS or too_long:
                report.warnings.append(
                    f"{scene.id}: plano {shot.kind} ({shot.anchor!r}) com ~{ms / 1000:.1f} s"
                )
            elif ms < READING_MS and _needs_reading_time(shot):
                report.warnings.append(
                    f"{scene.id}: {shot.kind} ({shot.anchor!r}) com ~{ms / 1000:.1f} s; "
                    f"precisa de {READING_MS / 1000:.0f} s para ser lido"
                )
            if isinstance(shot, MapShot) and region_codes is not None:
                for code in shot.highlight:
                    if code not in region_codes:
                        report.errors.append(f"{scene.id}: código {code} fora dos contornos do mapa")
            if isinstance(shot, QuoteShot) and excerpts:
                cited = [excerpts[e] for c in shot.claims for e in c.excerpt_ids if e in excerpts]
                if cited and not any(quote_in_excerpt(shot.text, text) for text in cited):
                    report.errors.append(
                        f"{scene.id}: citação na tela não está nos trechos citados: {shot.text!r}"
                    )
    report.warnings += variety_warnings(scenes.scenes)
    report.checked.append(
        f"scenes.json: {len(scenes.scenes)} cena(s), {shots} plano(s), ~{total_ms / 1000:.0f} s de narração "
        f"(média ~{total_ms / shots / 1000:.1f} s por plano, estimada)"
    )


def _needs_reading_time(shot: Shot) -> bool:
    return shot.kind in READING_KINDS or (isinstance(shot, QuoteShot) and shot.style == "document")


def number_errors(scene_id: str, shot: Shot, language: Language) -> list[str]:
    """Número na tela fora da convenção do idioma do episódio, ou que o template não sabe formatar nele
    (ADR 011, emenda "número por idioma"). Escrito errado, o hodômetro mostraria outro valor."""
    values: list[str] = []
    if isinstance(shot, NumberShot):
        values = [shot.value]
    elif isinstance(shot, CompareShot):
        values = [shot.left.value, shot.right.value]
    errors = [
        f"{scene_id}: {shot.kind} ({shot.anchor!r}): {problem}"
        for value in values
        if (problem := number_format_problem(value, language))
    ]
    if (
        language == "en"
        and isinstance(shot, ChartShot)
        and shot.type in BAR_TYPES
        and any(abs(p.value) >= BAR_PLAIN_BELOW or p.value != round(p.value) for p in shot.points)
    ):
        errors.append(
            f"{scene_id}: gráfico de barras ({shot.anchor!r}) em inglês com valor que o motion-kit fixado "
            "formata em pt-BR; use inteiros abaixo de mil ou outro tipo de gráfico"
        )
    return errors


def variety_warnings(scenes: list[Scene]) -> list[str]:
    """Cartões demais sem imagem, carimbos demais, tarja sem imagem, o mesmo tipo em sequência, gráfico de
    barras que devia ser comparação, frase na tela repetida (ADR 011, decisão 9)."""
    warnings: list[str] = []
    run: list[str] = []  # cenas do trecho atual de planos gráficos sem mídia
    total = stamps = 0
    previous: tuple[str, str] | None = None  # (cena, tipo) do plano gráfico anterior

    def close_run() -> None:
        if len(run) > MAX_GRAPHIC_RUN:
            where = run[0] if run[0] == run[-1] else f"{run[0]}–{run[-1]}"
            warnings.append(f"{where}: {len(run)} planos gráficos seguidos sem foto nem B-roll")
        run.clear()

    for scene in scenes:
        media_before = False
        keywords = 0
        for shot in effective_shots(scene):
            total += 1
            stamps += shot.kind == "stamp"
            keywords += shot.kind == "keyword"
            if shot.kind in MEDIA_SHOT_KINDS:
                media_before = True
                previous = None
                close_run()
                continue
            if shot.kind == "lower_third" and not media_before:
                warnings.append(f"{scene.id}: tarja ({shot.anchor!r}) sem foto nem B-roll por baixo")
            two_bars = isinstance(shot, ChartShot) and shot.type in ("bar", "bar_horizontal")
            if two_bars and len(shot.points) == 2:
                warnings.append(f"{scene.id}: gráfico de barras com 2 pontos ({shot.anchor!r}); use compare")
            if previous is not None and previous[1] == shot.kind:
                where = scene.id if previous[0] == scene.id else f"{previous[0]}–{scene.id}"
                warnings.append(f"{where}: {shot.kind} duas vezes seguidas")
            previous = (scene.id, shot.kind)
            if shot.kind in OVERLAY_SHOT_KINDS and media_before:
                close_run()  # desenhado sobre a mídia da cena: ainda há imagem na tela
            else:
                run.append(scene.id)
        if keywords > 1:
            warnings.append(f"{scene.id}: {keywords} frases na tela na mesma cena; use uma")
        media_before = False
    close_run()
    if total >= MIN_SHOTS_FOR_SHARE and stamps / total > MAX_STAMP_SHARE:
        warnings.append(
            f"carimbos em {stamps} de {total} planos ({stamps / total:.0%}); o limite é {MAX_STAMP_SHARE:.0%}"
        )
    return warnings


NEWS_MAX_AGE_DAYS = 30  # depois disso o fato não é mais notícia: o vídeo explica ou opina (ADR 019)


def objective_warnings(scenes: ScenesManifest, today: date | None = None) -> list[str]:
    """O objetivo do vídeo (ADR 019): alerta quando falta, e quando o fato noticiado já é velho."""
    objective = scenes.objective
    if objective is None:
        return ["roteiro sem objetivo declarado (noticiar, explicar ou opinar; ADR 019)"]
    if "noticiar" in objective.kinds and objective.event_date is not None and today is not None:
        age = (today - objective.event_date).days
        when = f"{objective.event_date:%d/%m/%Y}"
        if age < 0:
            return [f"objetivo noticiar com data no futuro ({when})"]
        if age > NEWS_MAX_AGE_DAYS:
            return [
                f"objetivo noticiar, mas o fato é de {when} ({age} dias): depois de {NEWS_MAX_AGE_DAYS} "
                "dias não é notícia; o vídeo explica ou opina"
            ]
    return []


def objective_summary(scenes: ScenesManifest) -> str | None:
    objective = scenes.objective
    if objective is None:
        return None
    return f"objetivo: {' + '.join(objective.kinds)}: {objective.promise}"


def _check_radar(
    store: ManifestStore,
    episode_id: str,
    scenes: ScenesManifest,
    report: CheckReport,
    chars_per_second: float,
    today: date | None,
) -> None:
    """Forma do roteiro contra o resumo do reels-radar, se o episódio tiver um (ADR 018). Só alertas: o
    resumo é observação de amostra pequena e nunca fonte de fato."""
    brief = _read(store, episode_id, BRIEF_FILE, RadarBrief, report)
    if brief is None:
        return
    caption_path = store.path(episode_id, CAPTION_FILE)
    caption = caption_path.read_text(encoding="utf-8") if caption_path.is_file() else None
    line = brief_summary(brief)
    unmeasured = unmeasured_patterns(scenes, brief, chars_per_second, caption)
    if unmeasured:
        line += f"; sem conferência no texto: {', '.join(unmeasured)}"
    report.checked.append(line)
    report.warnings += form_warnings(scenes, brief, chars_per_second, caption, today)


def check_episode(
    store: ManifestStore,
    episode_id: str,
    region_codes: frozenset[str] | None = None,
    chars_per_second: float = CHARS_PER_SECOND,
    today: date | None = None,
) -> CheckReport:
    """`region_codes`: códigos de país e estado que o template sabe desenhar (sem eles, não confere).
    `chars_per_second`: ritmo da voz configurada, para estimar a duração das cenas e dos planos.
    `today`: a data de hoje: diz se o resumo do radar está velho e se o fato noticiado ainda é notícia."""
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
        _check_scenes(scenes, sources, facts, excerpts, report, region_codes, chars_per_second)
        if (summary := objective_summary(scenes)) is not None:
            report.checked.append(summary)
        report.warnings += objective_warnings(scenes, today)
        _check_radar(store, episode_id, scenes, report, chars_per_second, today)
    if not report.checked and not report.errors:
        report.errors.append(f"nada para validar em {episode_id} (sources.json, facts.json, scenes.json)")
    return report
