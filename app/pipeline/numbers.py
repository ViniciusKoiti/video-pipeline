"""Números do roteiro gerados do `scenes.json` (#170) e comparados com o perfil de formato do nicho (ADR 031).

A parte numérica do `outline.md` (cenas, planos, pausas, "você", ritmo, alertas, quadros citados) sai daqui,
com as mesmas contas do `vp check`, num bloco entre marcadores que ninguém edita à mão
(`vp numeros <id> --escrever`). As medidas na unidade do nicho (trocas de imagem por minuto, "você" por
mil palavras...) seguem as definições do `analisar.py` da skill `analise-de-formato`, que mediu os vídeos do
nicho; o perfil medido chega ao episódio como `formato-brief.json` (cópia datada). É forma, nunca fonte
(§2.2): só informa e, num padrão forte, alerta.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.media.narration import pause_positions, strip_pauses, timeline_length
from app.pipeline.schemas import (
    CITATION_LICENSE,
    MEDIA_SHOT_KINDS,
    OVERLAY_SHOT_KINDS,
    Asset,
    BrollShot,
    PhotoShot,
    Scene,
    ScenesManifest,
    Shot,
    effective_shots,
)
from app.pipeline.shots import MIN_SHOT_MS, shot_bounds

MAX_SHOT_MS = 6000
# Sem teto de duração: a câmera percorre o plano (rede, cronologia) ou o vídeo se move sozinho e segurar a
# textura é o ritmo do formato (B-roll, ADR 031)
LONG_KINDS = frozenset({"network", "timeline", "broll"})
OPENING_SHARE = 0.10  # a abertura é o primeiro décimo da duração estimada (decisão D2 da spec)
OPENING_S = 60  # as medidas "_60s" do nicho olham o primeiro minuto
BLOCK_START = "<!-- números: gerado por `vp numeros`; não editar à mão -->"
BLOCK_END = "<!-- números: fim -->"
FORMAT_FILE = "formato-brief.json"
IMAGE_PLAN_FILE = "plano-imagens.md"
# As mesmas palavras que o `analisar.py` conta nos vídeos do nicho; o teste confere que não se separam.
SPOKEN = {
    "voce": re.compile(r"\b(você|vocês)\b", re.I),
    "nos": re.compile(r"\b(a gente|nós|nosso|nossa|nossos|nossas)\b", re.I),
    "eu": re.compile(r"\b(eu|meu|minha|pra mim|para mim|acho)\b", re.I),
    "fonte": re.compile(
        r"\b(segundo|de acordo com|estudo|estudos|pesquisa|pesquisas|pesquisadores|artigo)\b", re.I
    ),
}
MEASURE_LABELS = {
    "duracao_s": "duração (s)",
    "palavras_min": "palavras por minuto",
    "cortes_min": "trocas de imagem por minuto",
    "plano_medio_s": "plano médio (s)",
    "voce_por_mil": '"você" por mil palavras',
    "nos_por_mil": '"a gente" por mil palavras',
    "eu_por_mil": '"eu" por mil palavras',
    "fonte_por_mil": "fonte citada por mil palavras",
    "palavras_60s": "palavras no primeiro minuto",
    "voce_60s": '"você" no primeiro minuto',
    "cortes_60s": "trocas de imagem no primeiro minuto",
}


@dataclass(frozen=True)
class ShotTiming:
    scene_id: str
    shot: Shot
    start_ms: float  # desde o começo do vídeo
    ms: float


def scene_duration_ms(scene: Scene, chars_per_second: float) -> float:
    return timeline_length(scene.narration) / chars_per_second * 1000


def scene_timings(scene: Scene, chars_per_second: float) -> list[tuple[Shot, int, int]]:
    """(plano, início na cena, duração) em ms, como o `vp check` conta; âncora fora de ordem → ValueError."""
    planned = effective_shots(scene)
    bounds = shot_bounds(scene.narration, planned, round(scene_duration_ms(scene, chars_per_second)))
    return [(shot, start, ms) for shot, (start, ms) in zip(planned, bounds, strict=True)]


def shot_timings(scenes: ScenesManifest, chars_per_second: float) -> list[ShotTiming]:
    out, offset = [], 0.0
    for scene in scenes.scenes:
        for shot, start, ms in scene_timings(scene, chars_per_second):
            out.append(ShotTiming(scene.id, shot, offset + start, ms))
        offset += scene_duration_ms(scene, chars_per_second)
    return out


def rhythm_alert(shot: Shot, ms: float) -> bool:
    """Plano curto demais ou, fora dos que seguram de propósito, longo demais (mesma regra do `vp check`)."""
    return ms < MIN_SHOT_MS or (ms > MAX_SHOT_MS and shot.kind not in LONG_KINDS)


def _asset_id(shot: Shot) -> str | None:
    return shot.asset_id if isinstance(shot, PhotoShot | BrollShot) else None


def image_changes(timings: Sequence[ShotTiming]) -> list[float]:
    """Início (ms) de cada troca do que se vê na tela inteira, como o corte que o ffmpeg conta no nicho.

    Troca: mídia com ativo diferente da anterior, ou plano gráfico que não fica sobre uma mídia. Planos
    seguidos do mesmo vídeo de textura (continuidade da ADR 031) e a tarja ou o número sobre a foto não trocam
    a tela."""
    changes, previous, media_on = [], object(), False
    for timing in timings:
        shot = timing.shot
        if shot.kind in MEDIA_SHOT_KINDS:
            asset = _asset_id(shot)
            if asset is None or asset != previous:
                changes.append(timing.start_ms)
            previous, media_on = asset, True
        elif shot.kind in OVERLAY_SHOT_KINDS and media_on:
            continue
        else:
            changes.append(timing.start_ms)
            previous = object()
    return changes


@dataclass(frozen=True)
class Citation:
    scene_id: str
    anchor: str
    asset_id: str
    ms: float


@dataclass(frozen=True)
class ScriptNumbers:
    scenes: int
    shots: int
    text_shots: int
    pauses: int
    words: int
    duration_ms: float
    voce: int
    voce_scenes: int
    voce_closing: int
    opening: tuple[int, float]  # planos que começam no primeiro décimo, e a duração desse décimo (ms)
    rest: tuple[int, float]
    rhythm_alerts: list[ShotTiming]
    citations: list[Citation]
    assets_by_use: dict[str, list[str]]  # ativo -> cenas, na ordem da primeira aparição
    unused_assets: list[str]
    measures: dict[str, float] = field(default_factory=dict)  # as medidas na unidade do nicho


def _plain(scenes: ScenesManifest) -> list[tuple[str, str]]:
    return [(scene.id, strip_pauses(scene.narration)) for scene in scenes.scenes]


def niche_measures(
    scenes: ScenesManifest, timings: Sequence[ShotTiming], chars_per_second: float
) -> dict[str, float]:
    """As colunas do `tercos.csv` do nicho, calculadas no roteiro (duração estimada, não a dos WAVs)."""
    texts = [text for _, text in _plain(scenes)]
    words = sum(len(text.split()) for text in texts)
    duration_s = sum(scene_duration_ms(s, chars_per_second) for s in scenes.scenes) / 1000
    changes = image_changes(timings)
    opening, offset = [], 0.0
    for scene, text in zip(scenes.scenes, texts, strict=True):
        if offset < OPENING_S * 1000:
            opening.append(text)
        offset += scene_duration_ms(scene, chars_per_second)
    joined, first = " ".join(texts), " ".join(opening)
    if not words or not duration_s:
        return {}
    per_thousand = {f"{name}_por_mil": len(rx.findall(joined)) / words * 1000 for name, rx in SPOKEN.items()}
    return {
        "duracao_s": duration_s,
        "palavras_min": words / duration_s * 60,
        "cortes_min": len(changes) / duration_s * 60,
        "plano_medio_s": duration_s / len(changes) if changes else duration_s,
        **per_thousand,
        "palavras_60s": len(first.split()),
        "voce_60s": len(SPOKEN["voce"].findall(first)),
        "cortes_60s": sum(1 for start in changes if start < OPENING_S * 1000),
    }


def script_numbers(
    scenes: ScenesManifest, assets: Mapping[str, Asset], chars_per_second: float
) -> ScriptNumbers:
    timings = shot_timings(scenes, chars_per_second)
    plain = _plain(scenes)
    total_ms = sum(scene_duration_ms(s, chars_per_second) for s in scenes.scenes)
    positions, cursor, scenes_with = [], 0, set()
    for scene_id, text in plain:
        for match in SPOKEN["voce"].finditer(text):
            positions.append(cursor + match.start())
            scenes_with.add(scene_id)
        cursor += len(text) + 1
    closing_from = 0.9 * max(cursor - 1, 0)
    opening_ms = OPENING_SHARE * total_ms
    in_opening = sum(1 for t in timings if t.start_ms < opening_ms)
    used: dict[str, list[str]] = {}
    for timing in timings:
        asset = _asset_id(timing.shot)
        if asset and timing.scene_id not in used.setdefault(asset, []):
            used[asset].append(timing.scene_id)
    citations = [
        Citation(t.scene_id, t.shot.anchor, asset, t.ms)
        for t in timings
        if isinstance(t.shot, PhotoShot)
        and (asset := t.shot.asset_id) is not None
        and asset in assets
        and assets[asset].license_id == CITATION_LICENSE
    ]
    return ScriptNumbers(
        scenes=len(scenes.scenes),
        shots=len(timings),
        text_shots=sum(1 for t in timings if t.shot.kind not in MEDIA_SHOT_KINDS),
        pauses=sum(len(pause_positions(s.narration)) for s in scenes.scenes),
        words=sum(len(text.split()) for _, text in plain),
        duration_ms=total_ms,
        voce=len(positions),
        voce_scenes=len(scenes_with),
        voce_closing=sum(1 for p in positions if p >= closing_from),
        opening=(in_opening, opening_ms),
        rest=(len(timings) - in_opening, total_ms - opening_ms),
        rhythm_alerts=[t for t in timings if rhythm_alert(t.shot, t.ms)],
        citations=citations,
        assets_by_use=used,
        unused_assets=sorted(set(assets) - set(used)),
        measures=niche_measures(scenes, timings, chars_per_second),
    )


# --- perfil de formato do nicho (ADR 031, parte B) ---


class _Brief(BaseModel):
    # O contrato é da skill `analise-de-formato` e pode ganhar campos: o que não é lido aqui é ignorado.
    model_config = ConfigDict(extra="ignore", frozen=True, populate_by_name=True)


class FormatMeasure(_Brief):
    alto: float  # mediana do terço de mais views
    baixo: float  # mediana do terço de menos views
    rho: float | None = None  # Spearman com log das views
    n: int
    forca: Literal["pattern", "hint"]

    def bottom_side(self, value: float) -> bool:
        """O valor do roteiro está mais perto do terço de baixo que do de cima."""
        return abs(value - self.baixo) < abs(value - self.alto)


class FormatBrief(_Brief):
    schema_name: Literal["formato_brief.v1"] = Field(alias="schema")
    nicho: str
    grupo: str
    data: date
    n: int
    medidas: dict[str, FormatMeasure]


def format_warnings(numbers: ScriptNumbers, brief: FormatBrief | None) -> list[str]:
    """Só padrões fortes (`pattern`) geram alerta, e só quando o roteiro está do lado do terço de baixo."""
    if brief is None:
        return []
    out = []
    for name, measure in brief.medidas.items():
        value = numbers.measures.get(name)
        if value is None or measure.forca != "pattern" or not measure.bottom_side(value):
            continue
        rho = f", ρ {_num(measure.rho, 2)}" if measure.rho is not None else ""
        out.append(
            f"formato: {MEASURE_LABELS.get(name, name)} = {_num(value)}; o terço de cima do nicho tem "
            f"{_num(measure.alto)} e o de baixo {_num(measure.baixo)} (pattern{rho}, perfil de {brief.data})"
        )
    return out


# --- texto gerado ---


def _num(value: float | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    text = f"{value:,.{decimals}f}" if decimals else f"{value:,.0f}"
    return text.replace(",", "§").replace(".", ",").replace("§", ".")


def _seconds(ms: float) -> str:
    return f"~{_num(ms / 1000)} s"


def _per_minute(count: int, ms: float) -> str:
    return _num(count / ms * 60000) if ms else "—"


def render_block(numbers: ScriptNumbers, brief: FormatBrief | None, chars_per_second: float) -> str:
    n = numbers
    minutes = n.duration_ms / 60000
    lines = [
        BLOCK_START,
        "## Números do roteiro (gerado)",
        "",
        f"Estimativa a {_num(chars_per_second)} caracteres por segundo, a mesma do `vp check`; o tempo real "
        "sai dos WAVs.",
        "",
        f"- {n.scenes} cenas, {n.shots} planos ({n.text_shots} com texto), {n.pauses} pausas, "
        f"{_num(n.words, 0)} palavras, ~{_num(n.duration_ms / 1000, 0)} s (~{_num(minutes, 0)} min).",
        f'- "você": {n.voce} vezes em {n.voce_scenes} cenas; {n.voce_closing} no último décimo.',
        f"- Ritmo: abertura (primeiro décimo) com {n.opening[0]} planos em {_seconds(n.opening[1])} "
        f"(~{_per_minute(n.opening[0], n.opening[1])} por minuto); o resto com {n.rest[0]} planos em "
        f"{_seconds(n.rest[1])} (~{_per_minute(n.rest[0], n.rest[1])} por minuto).",
        f"- Alertas de ritmo do `vp check` ({len(n.rhythm_alerts)}):"
        + ("" if n.rhythm_alerts else " nenhum."),
    ]
    lines += [f'  - {t.scene_id} {t.shot.kind} "{t.shot.anchor}" {_seconds(t.ms)}' for t in n.rhythm_alerts]
    distinct = len({c.asset_id for c in n.citations})
    lines += ["", f"### Quadros citados (`Citacao`): {len(n.citations)} usos de {distinct} ativos", ""]
    if n.citations:
        lines += ["| # | Cena | Âncora | Ativo | Tempo |", "|---|---|---|---|---|"]
        lines += [
            f'| {i} | {c.scene_id} | "{c.anchor}" | `{c.asset_id}` | {_seconds(c.ms)} |'
            for i, c in enumerate(n.citations, 1)
        ]
    lines += ["", f"### Ativos usados: {len(n.assets_by_use)}", ""]
    if n.unused_assets:
        lines.append("Baixados e fora do vídeo: " + ", ".join(f"`{a}`" for a in n.unused_assets) + ".")
    lines += ["", "### Formato × nicho", ""]
    if brief is None:
        lines.append(f"Sem `{FORMAT_FILE}` no episódio: nada a comparar.")
    else:
        lines += [
            f"Perfil de {brief.data}, {brief.nicho}, grupo {brief.grupo}, n = {brief.n}. Medidas do roteiro "
            "na unidade do nicho; é forma, nunca fonte.",
            "",
            "| Medida | Roteiro | Terço de cima | Terço de baixo | Força |",
            "|---|---|---|---|---|",
        ]
        for name, measure in brief.medidas.items():
            ours = n.measures.get(name)
            rho = f" (ρ {_num(measure.rho, 2)})" if measure.rho is not None else ""
            lines.append(
                f"| {MEASURE_LABELS.get(name, name)} | {_num(ours)} | {_num(measure.alto)} | "
                f"{_num(measure.baixo)} | {measure.forca}{rho} |"
            )
    lines += ["", BLOCK_END]
    return "\n".join(lines)


def current_block(text: str) -> str | None:
    start, end = text.find(BLOCK_START), text.find(BLOCK_END)
    if start < 0 or end < start:
        return None
    return text[start : end + len(BLOCK_END)]


def replace_block(text: str, block: str) -> str:
    """O texto com o bloco trocado; sem bloco, acrescenta no fim. O que está fora dos marcadores não muda."""
    old = current_block(text)
    if old is not None:
        return text.replace(old, block, 1)
    return text.rstrip("\n") + "\n\n" + block + "\n"


def strip_block(data: bytes) -> bytes:
    """Os bytes sem o bloco gerado: o carimbo do gate 2 e o do parecer não dependem dele (decisão D1).

    Sem bloco, os bytes voltam iguais. Com bloco, sai também a linha em branco que o `replace_block` põe antes
    dele: o outline aprovado antes do bloco tem o mesmo carimbo depois de ganhá-lo."""
    start, end = data.find(BLOCK_START.encode()), data.find(BLOCK_END.encode())
    if start < 0 or end < start:
        return data
    before, after = data[:start].rstrip(b"\n"), data[end + len(BLOCK_END.encode()) :]
    if not after.strip():
        return before + b"\n"
    return before + b"\n\n" + after.lstrip(b"\n")


def render_image_plan(
    scenes: ScenesManifest, numbers: ScriptNumbers, assets: Mapping[str, Asset], chars_per_second: float
) -> str:
    lines = [
        f"# Plano de imagens: {scenes.episode_id}",
        "",
        "Gerado por `vp numeros --escrever` a partir do `scenes.json` e de `assets/*.json`; não editar à "
        "mão. "
        f"Tempos estimados a {_num(chars_per_second)} caracteres por segundo.",
        "",
        "| Cena | Tempo | Âncora | Tipo | Ativo | Licença |",
        "|---|---|---|---|---|---|",
    ]
    for timing in shot_timings(scenes, chars_per_second):
        asset = _asset_id(timing.shot)
        clock = f"{int(timing.start_ms // 60000)}:{int(timing.start_ms % 60000 // 1000):02d}"
        if timing.shot.kind in MEDIA_SHOT_KINDS:
            license_id = assets[asset].license_id if asset in assets else "sem registro"
            shown = f"`{asset}`" if asset else "(sem ativo)"
        else:
            license_id, shown = "—", "(gráfico do template)"
        shot = timing.shot
        row = (timing.scene_id, clock, shot.anchor, shot.kind, shown, license_id)
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", f"## Ativos usados ({len(numbers.assets_by_use)})", "", "| Ativo | Licença | Cenas |"]
    lines.append("|---|---|---|")
    for asset, used_in in sorted(numbers.assets_by_use.items()):
        license_id = assets[asset].license_id if asset in assets else "sem registro"
        lines.append(f"| `{asset}` | {license_id} | {', '.join(used_in)} |")
    if numbers.unused_assets:
        lines += ["", "Baixados e fora do vídeo (motivo no `usage_notes`): "]
        lines[-1] += ", ".join(f"`{a}`" for a in numbers.unused_assets) + "."
    return "\n".join(lines) + "\n"


def used_in_scenes_mismatches(numbers: ScriptNumbers, assets: Mapping[str, Asset]) -> dict[str, list[str]]:
    """Ativos cujo `used_in_scenes` não bate com o roteiro -> as cenas certas."""
    return {
        asset_id: numbers.assets_by_use.get(asset_id, [])
        for asset_id, asset in assets.items()
        if list(asset.used_in_scenes) != numbers.assets_by_use.get(asset_id, [])
    }
