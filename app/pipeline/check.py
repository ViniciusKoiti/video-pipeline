"""`vp check`: valida o que agentes ou pessoas escreveram, sem chamar modelo nenhum (ADR 009).

Confere, no que existir na pasta do episódio: `sources.json` e os textos extraídos; `facts.json` (cada
citação é literal e está no trecho citado; fontes independentes); `scenes.json` (schema, âncoras, fontes
e trechos das afirmações, uso só de fatos fichados, ritmo estimado pela narração). Erro bloqueia o gate;
alerta vai para a revisão humana.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date

from pydantic import ValidationError

from app.media.narration import strip_pauses, timeline_length
from app.pipeline.excerpts import excerpts_of, quote_in_excerpt
from app.pipeline.molde import MOLDE_FILE, Molde, claimless_statements, molde_summary, molde_warnings
from app.pipeline.music import plan_problems
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
    MUSIC_PLAN_FILE,
    NUMBER_SEPARATORS,
    OVERLAY_SHOT_KINDS,
    Asset,
    BrollShot,
    CalculationShot,
    ChartShot,
    CompareShot,
    EndCardShot,
    FactKind,
    FactsManifest,
    Language,
    MapShot,
    MusicCatalog,
    MusicPlan,
    NumberShot,
    PhotoShot,
    QuoteShot,
    ReceiptShot,
    Scene,
    ScenesManifest,
    Shot,
    SourceKind,
    SourcesManifest,
    citation_violations,
    effective_shots,
    number_format_problem,
    screen_number,
    screen_parts,
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
READING_KINDS = frozenset({"chart", "compare", "network", "timeline", "calculation", "receipt"})
# Sem teto de duração: a câmera percorre o plano (rede, cronologia) ou o vídeo se move sozinho e segurar a
# textura é o ritmo do formato (B-roll, ADR 031)
LONG_KINDS = frozenset({"network", "timeline", "broll"})
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


def _assets(
    store: ManifestStore, episode_id: str, planned: list[tuple[str, Shot, float]], report: CheckReport
) -> dict[str, Asset]:
    """Ativos já registrados (`assets/<id>.json`) dos planos de foto e B-roll; o não escolhido fica fora."""
    media = (shot for _, shot, _ in planned if isinstance(shot, PhotoShot | BrollShot))
    ids = {shot.asset_id for shot in media if shot.asset_id}
    found = {}
    for asset_id in sorted(ids):
        if (asset := _read(store, episode_id, f"assets/{asset_id}.json", Asset, report)) is not None:
            found[asset_id] = asset
    return found


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
) -> list[tuple[str, Shot, float]]:
    """Valida as cenas e devolve cada plano com a duração estimada, para as regras que dependem dos ativos."""
    planned_ms: list[tuple[str, Shot, float]] = []
    if sources is not None:
        report.errors += unknown_source_refs(scenes, sources)
    fact_excerpts = {e.excerpt_id for f in facts.facts for e in f.evidence} if facts else set()
    # sem objetivo declarado (já é alerta), a conta não é recusada por ele
    explains = scenes.objective is None or "explicar" in scenes.objective.kinds
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
            planned_ms.append((scene.id, shot, ms))
            report.warnings += text_fit_warnings(
                scene.id, shot, ms, media_before and shot.kind in OVERLAY_SHOT_KINDS
            )
            report.errors += number_errors(scene.id, shot, scenes.language)
            report.errors += arithmetic_errors(scene.id, shot, scenes.language)
            computed = isinstance(shot, CalculationShot) or (isinstance(shot, ReceiptShot) and shot.total)
            if computed and not explains:
                report.errors.append(
                    f"{scene.id}: {shot.kind} ({shot.anchor!r}): conta na tela só em vídeo que explica "
                    "(ADR 020)"
                )
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
    return planned_ms


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
    elif isinstance(shot, CalculationShot):
        values = [term.text for term in shot.terms] + [shot.result.text]
    elif isinstance(shot, ReceiptShot):
        values = [item.value for item in shot.items] + ([shot.total.value] if shot.total else [])
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


def _amount(text: str, language: Language) -> tuple[float, int, str, str] | None:
    """(valor, casas decimais, prefixo, sufixo) de um número na tela; "20%" vale 0,2 numa conta."""
    parts, number = screen_parts(text), screen_number(text, language)
    if parts is None or number is None:
        return None
    prefix, value, suffix = number
    _, separator, fraction = parts[1].partition(NUMBER_SEPARATORS[language][1])
    decimals = len(fraction) if separator else 0
    return (value / 100 if suffix.startswith("%") else value), decimals, prefix, suffix


def _written(value: float, decimals: int, language: Language) -> str:
    """Número com as casas e o separador decimal do idioma, para a mensagem."""
    return f"{value:.{decimals}f}".replace(".", NUMBER_SEPARATORS[language][1])


def _evaluate(values: list[float], operators: list[str]) -> float:
    """A conta como se escreve: × e ÷ antes de + e −, da esquerda para a direita."""
    terms, signs = [values[0]], []
    for op, value in zip(operators, values[1:], strict=True):
        if op == "×":
            terms[-1] *= value
        elif op == "÷":
            terms[-1] /= value
        else:
            signs.append(op)
            terms.append(value)
    total = terms[0]
    for op, value in zip(signs, terms[1:], strict=True):
        total = total + value if op == "+" else total - value
    return total


def _shown(value: float, decimals: int, suffix: str) -> float:
    """O valor como a tela o escreve: em porcentagem, ×100; arredondado nas casas que ela mostra."""
    return round(value * 100 if suffix.startswith("%") else value, decimals)


def arithmetic_errors(scene_id: str, shot: Shot, language: Language) -> list[str]:
    """A tela não calcula, mas o `vp check` refaz a conta (ADR 020, item 4; ADR 028): o resultado da conta e
    o total da nota têm de ser o que os números escritos dão, arredondados como a tela mostra."""
    where = f"{scene_id}: {shot.kind} ({shot.anchor!r})"
    if isinstance(shot, CalculationShot):
        texts = [term.text for term in shot.terms] + [shot.result.text]
        amounts = [_amount(text, language) for text in texts]
        missing = [text for text, amount in zip(texts, amounts, strict=True) if amount is None]
        if missing:
            return [f"{where}: sem número para refazer a conta: {', '.join(map(repr, missing))}"]
        values = [a[0] for a in amounts if a is not None]
        try:
            got = _evaluate(values[:-1], [term.op or "" for term in shot.terms[1:]])
        except ZeroDivisionError:
            return [f"{where}: divisão por zero"]
        _, decimals, _, suffix = amounts[-1]  # type: ignore[misc]
        expected = _shown(got, decimals, suffix)
        if abs(expected - _shown(values[-1], decimals, suffix)) > 10**-decimals / 2:
            expression = " ".join(
                [shot.terms[0].text] + [f"{term.op} {term.text}" for term in shot.terms[1:]]
            )
            return [f"{where}: {expression} dá {_written(expected, decimals, language)}, e a tela mostra "
                    f"{shot.result.text}"]
        return []
    if isinstance(shot, ReceiptShot):
        rows = [item.value for item in shot.items] + ([shot.total.value] if shot.total else [])
        amounts = [_amount(text, language) for text in rows]
        if any(amount is None for amount in amounts):
            return [f"{where}: linha da nota sem número"]
        units = {(a[2], a[3]) for a in amounts if a is not None}
        if len(units) > 1:
            return [f"{where}: linhas em unidades diferentes: {', '.join(map(repr, rows))}"]
        if shot.total is not None:
            *items, (total, decimals, _, _) = [a for a in amounts if a is not None]
            got = round(sum(item[0] for item in items), decimals)
            if abs(got - round(total, decimals)) > 10**-decimals / 2:
                return [f"{where}: as linhas somam {_written(got, decimals, language)}, e o total mostra "
                        f"{shot.total.value}"]
        return []
    return []


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


# O que a chamada de cada estágio pede (ADR 026), como começo de palavra sem acento: "salva", "salvar" e
# "salve" valem para "salv". Chamada sem nenhum deles pede outra coisa que o estágio, e gera alerta.
FUNNEL_ASKS: dict[str, tuple[str, tuple[str, ...]]] = {
    "topo": ("seguir ou compartilhar", ("segu", "compartilh", "manda", "envia")),
    "meio": ("salvar ou comentar", ("salv", "coment")),
    "fundo": ("pedir o que é oferecido", ("coment", "link", "bio", "direct", "ped", "baix", "chama")),
}
# A variante do cartão final por estágio (ADR 028); `next` vale em qualquer um, quando a série continua. O
# fundo ainda não tem variante (decisão 4): o contrato recusa o cartão final nele.
END_CARD_VARIANTS = {"topo": "follow", "meio": "save"}


def _words(text: str) -> list[str]:
    decomposed = unicodedata.normalize("NFD", strip_pauses(text).lower())
    plain = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", plain)


def _contains(words: list[str], part: list[str]) -> bool:
    return any(words[i : i + len(part)] == part for i in range(len(words) - len(part) + 1))


def funnel_warnings(scenes: ScenesManifest) -> list[str]:
    """O estágio do funil (ADR 026): alerta quando falta, quando a chamada não pede o que o estágio pede e
    quando ela não está na narração da última cena."""
    funnel = scenes.funnel
    if funnel is None:
        return ["roteiro sem estágio do funil (topo, meio ou fundo; ADR 026)"]
    warnings = []
    asks, starts = FUNNEL_ASKS[funnel.stage]
    cta = _words(funnel.cta)
    if not any(word.startswith(starts) for word in cta):
        warnings.append(f"funil {funnel.stage}: a chamada \"{funnel.cta}\" não pede para {asks}")
    last = scenes.scenes[-1]
    if not _contains(_words(last.narration), cta):
        warnings.append(f"funil: a chamada \"{funnel.cta}\" não está na narração da última cena ({last.id})")
    card = last.shots[-1] if last.shots and isinstance(last.shots[-1], EndCardShot) else None
    if card is not None:
        expected = END_CARD_VARIANTS.get(funnel.stage)
        if card.variant != "next" and card.variant != expected:
            warnings.append(f"funil {funnel.stage}: cartão final {card.variant}; o estágio pede {expected}")
        spoken = strip_pauses(last.narration)
        if not _contains(_words(spoken[spoken.find(card.anchor):]), cta):
            warnings.append(
                f"funil: a chamada \"{funnel.cta}\" não é dita durante o cartão final ({last.id})"
            )
    return warnings


def funnel_summary(scenes: ScenesManifest) -> str | None:
    funnel = scenes.funnel
    if funnel is None:
        return None
    line = f"funil: {funnel.stage}; chamada: {funnel.cta}"
    return f"{line}; oferta: {funnel.offer}" if funnel.offer else line


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


def _check_molde(
    store: ManifestStore,
    episode_id: str,
    scenes: ScenesManifest,
    report: CheckReport,
    chars_per_second: float,
) -> None:
    """Forma do roteiro longo contra o molde do nicho copiado no episódio pela partitura (ADR 031). Só
    alertas: o molde é descrição de amostra e nunca fonte de fato."""
    molde = _read(store, episode_id, MOLDE_FILE, Molde, report)
    if molde is None:
        return
    report.checked.append(molde_summary(molde))
    report.warnings += molde_warnings(scenes, molde, chars_per_second)


def _check_music(
    store: ManifestStore,
    episode_id: str,
    scenes: ScenesManifest,
    catalog: MusicCatalog | None,
    report: CheckReport,
    chars_per_second: float,
) -> None:
    """Plano da trilha (ADR 030), quando o episódio tem `music.json`."""
    plan = _read(store, episode_id, MUSIC_PLAN_FILE, MusicPlan, report)
    if plan is None:
        return
    if catalog is None:
        report.errors.append("music.json sem catálogo de faixas (data/music/catalog.json)")
        return
    minutes = sum(timeline_length(s.narration) for s in scenes.scenes) / chars_per_second / 60
    errors, warnings = plan_problems(plan, scenes.scenes, catalog, minutes)
    report.errors += errors
    report.warnings += warnings
    tracks = sorted({cue.track for cue in plan.cues if cue.track})
    report.warnings += [
        f"music.json: faixa {t} ainda sem cópia no episódio (assets/{t}.json, gate 3)"
        for t in tracks
        if not store.exists(episode_id, f"assets/{t}.json")
    ]
    if not errors:
        report.checked.append(f"trilha: {len(plan.cues)} entrada(s), {len(tracks)} faixa(s)")


def check_episode(
    store: ManifestStore,
    episode_id: str,
    region_codes: frozenset[str] | None = None,
    chars_per_second: float = CHARS_PER_SECOND,
    today: date | None = None,
    music_catalog: MusicCatalog | None = None,
) -> CheckReport:
    """`region_codes`: códigos de país e estado que o template sabe desenhar (sem eles, não confere).
    `chars_per_second`: ritmo da voz configurada, para estimar a duração das cenas e dos planos.
    `today`: a data de hoje: diz se o resumo do radar está velho e se o fato noticiado ainda é notícia.
    `music_catalog`: as faixas que o plano da trilha pode usar (ADR 030)."""
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
        planned = _check_scenes(scenes, sources, facts, excerpts, report, region_codes, chars_per_second)
        report.errors += citation_violations(planned, _assets(store, episode_id, planned, report))
        if (summary := objective_summary(scenes)) is not None:
            report.checked.append(summary)
        report.warnings += objective_warnings(scenes, today)
        if (summary := funnel_summary(scenes)) is not None:
            report.checked.append(summary)
        report.warnings += funnel_warnings(scenes)
        report.warnings += claimless_statements(scenes)
        _check_radar(store, episode_id, scenes, report, chars_per_second, today)
        _check_molde(store, episode_id, scenes, report, chars_per_second)
        _check_music(store, episode_id, scenes, music_catalog, report, chars_per_second)
    if not report.checked and not report.errors:
        report.errors.append(f"nada para validar em {episode_id} (sources.json, facts.json, scenes.json)")
    return report
