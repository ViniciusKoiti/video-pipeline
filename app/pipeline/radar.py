"""Resumo do reels-radar como entrada de FORMA do roteiro (ADR 018).

O reels-radar (projeto à parte) lê Reels de um nicho e grava `briefs/<nicho>.json` (`script_brief.v1`): que
características de forma andam com mais ou menos na medida da plataforma (`measure`: compartilhamentos por
visualização no Instagram; curtidas por visualização no YouTube Shorts, que não mostra compartilhamentos). Uma
cópia datada fica na pasta do episódio (`radar-brief.json`); aqui ela é lida e comparada com o roteiro.
É observação de amostra pequena, nunca fonte de fato (§2.2): só gera alertas, e só do que dá para medir no
texto. O que depende de olhar o vídeo (pessoa falando para a câmera, tom de alerta) fica para a skill de
roteiro e para a revisão humana.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.media.narration import strip_pauses, timeline_length
from app.pipeline.schemas import ScenesManifest

BRIEF_FILE = "radar-brief.json"
CAPTION_FILE = "legenda-post.txt"
MAX_AGE_DAYS = 45  # depois disso o resumo descreve Reels que já saíram de circulação
OPENING_SHOTS = 2  # o título de alerta conta se for um dos primeiros planos da primeira cena
MIN_ANALYSED = 30  # abaixo disso o resumo leu poucos Reels e os padrões ficam como hipótese (skill `pauta`)

# `measure` do resumo -> como o alerta a chama. Resumo antigo não tem o campo, e a medida fica desconhecida.
MEASURES = {
    "shares/views": "compartilhamentos por visualização",
    "likes/views": "curtidas por visualização",
    "comments/views": "comentários por visualização",
}

_VIEWER = {
    "pt-BR": r"\b(você|vocês|seu|sua|seus|suas|teu|tua|teus|tuas|contigo)\b",
    "en": r"\b(you|your|yours)\b",
}
_SENTENCE_END = re.compile(r"(?<=[.?!…])\s+")
_EMOJI = re.compile("[\U0001f000-\U0001faff☀-➿⬀-⯿]")
_ASKS_COMMENT = re.compile(r"coment|comment", re.IGNORECASE)


class _Radar(BaseModel):
    # O contrato é do reels-radar e pode ganhar campos: o que não é lido aqui é ignorado.
    model_config = ConfigDict(extra="ignore", frozen=True, populate_by_name=True)


class RadarGuidance(_Radar):
    about: str  # form | opening | video | engagement | theme
    trait: str
    advice: Literal["use", "avoid"]
    strength: Literal["pattern", "hint"]  # pattern: 5+ Reels de cada lado e acaso até 10%; hint: até 30%
    share_rate_with: float | None = None
    share_rate_without: float | None = None
    n_with: int
    n_without: int
    chance: float


class RadarPurposes(_Radar):
    """Que tipo de vídeo (notícia, explicação, opinião) anda mais no nicho, quando o radar fez essa leitura.
    Vem das palavras soltas das legendas, com o léxico do idioma de cada Reel: é palpite de vocabulário."""

    reader: str
    read: int  # quantos Reels tiveram a legenda lida
    main_purposes: dict[str, int] = {}  # tipo principal (ou "none") -> Reels
    guidance: list[RadarGuidance] = []  # `purpose_news`, `purpose_explain`, `purpose_opinion`
    no_basis: list[str] = []


# tipo do radar -> objetivo do roteiro (ADR 019)
PURPOSE_KINDS = {"purpose_news": "noticiar", "purpose_explain": "explicar", "purpose_opinion": "opinar"}


class RadarBrief(_Radar):
    schema_name: Literal["script_brief.v1"] = Field(alias="schema")
    niche: str
    generated_at: datetime
    analysed: int  # quantos Reels foram lidos
    measure: str | None = None  # taxa de todos os números (shares/views, likes/views); resumo antigo não tem
    guidance: list[RadarGuidance] = []
    themes: list[RadarGuidance] = []  # palavras soltas das legendas: pergunta para a pesquisa, nunca fato
    thresholds: dict[str, float | None] = {}  # None: o nicho não deu base para esse corte
    caveats: list[str] = []
    purposes: RadarPurposes | None = None  # resumos antigos não têm

    def patterns(self) -> list[RadarGuidance]:
        """Os padrões de forma e, quando o radar leu os tipos, os de tipo de vídeo."""
        about_kind = self.purposes.guidance if self.purposes else []
        return [g for g in [*self.guidance, *about_kind] if g.strength == "pattern"]

    def hints(self) -> list[RadarGuidance]:
        return [g for g in self.guidance if g.strength == "hint"]

    def threshold(self, key: str) -> float | None:
        """O corte de um `long_*` neste nicho, ou None quando o resumo não tem base para ele."""
        return self.thresholds.get(key)

    def measure_label(self) -> str:
        """A medida, como o alerta a chama: nunca 'compartilhamento' quando o resumo mediu outra coisa."""
        if self.measure is None:
            return "na medida do resumo, que não está informada"
        return MEASURES.get(self.measure, self.measure)


def brief_summary(brief: RadarBrief) -> str:
    return (
        f"{BRIEF_FILE}: nicho {brief.niche}, {brief.analysed} Reels lidos, de {brief.generated_at:%d/%m/%Y}; "
        f"{len(brief.patterns())} padrão(ões) e {len(brief.hints())} indício(s) de forma; "
        + ("medida não informada (resumo antigo)" if brief.measure is None
           else f"medida: {brief.measure_label()}")
        + (_purposes_summary(brief.purposes) if brief.purposes else "")
    )


def _purposes_summary(purposes: RadarPurposes) -> str:
    names = {"news": "notícia", "explain": "explicação", "opinion": "opinião", "none": "sem sinal"}
    counts = ", ".join(f"{names.get(kind, kind)} {n}" for kind, n in purposes.main_purposes.items())
    return f"; tipos lidos em {purposes.read} Reels ({counts})"


def opening_sentence(scenes: ScenesManifest) -> str:
    """A primeira frase falada do vídeo, sem as marcas de pausa."""
    text = strip_pauses(scenes.scenes[0].narration).strip()
    return _SENTENCE_END.split(text, maxsplit=1)[0]


def _rates(g: RadarGuidance) -> str:
    if g.share_rate_with is None or g.share_rate_without is None:
        return f"n={g.n_with}/{g.n_without}"
    with_, without = f"{g.share_rate_with:.1%}", f"{g.share_rate_without:.1%}"
    return f"{with_} com × {without} sem, n={g.n_with}/{g.n_without}".replace(".", ",")


def _measured(
    trait: str,
    scenes: ScenesManifest,
    brief: RadarBrief,
    chars_per_second: float,
    caption: str | None,
) -> tuple[bool, str] | None:
    """(o roteiro tem a característica?, o que foi medido) ou None quando o código não sabe medir."""
    opening = opening_sentence(scenes)
    if trait in PURPOSE_KINDS:
        if scenes.objective is None:
            return None  # sem objetivo declarado não há o que comparar; o `vp check` já avisa disso
        kinds = scenes.objective.kinds
        return PURPOSE_KINDS[trait] in kinds, f"o objetivo declarado é {' + '.join(kinds)}"
    if trait == "long_video" and (limit := brief.threshold("long_video_above_s")) is not None:
        seconds = sum(timeline_length(s.narration) for s in scenes.scenes) / chars_per_second
        return seconds > limit, f"o roteiro tem ~{seconds:.0f} s e o corte é {limit:.0f} s"
    if trait == "addresses_viewer" and scenes.language in _VIEWER:
        found = re.search(_VIEWER[scenes.language], opening, re.IGNORECASE) is not None
        return found, f"abertura: {opening!r}"
    if trait == "opens_question":
        return opening.rstrip().endswith("?"), f"abertura: {opening!r}"
    if trait == "long_opening" and (limit := brief.threshold("long_opening_above_words")) is not None:
        words = len(opening.split())
        return words > limit, f"a abertura tem {words} palavras e o corte é {limit:.0f}"
    if trait == "screen_alert":
        kinds = [shot.kind for shot in scenes.scenes[0].shots[:OPENING_SHOTS]]
        return "keyword" in kinds, f"primeiros planos: {', '.join(kinds) or 'nenhum'}"
    if caption is not None:
        first_line = caption.strip().splitlines()[0] if caption.strip() else ""
        if trait == "has_emoji":
            return _EMOJI.search(first_line) is not None, f"primeira linha da legenda: {first_line!r}"
        if trait == "ask_comment":
            return _ASKS_COMMENT.search(caption) is not None, "legenda do post"
        if trait == "long_caption" and (limit := brief.threshold("long_caption_above_words")) is not None:
            words = len(caption.split())
            return words > limit, f"a legenda tem {words} palavras e o corte é {limit:.0f}"
    return None


def form_warnings(
    scenes: ScenesManifest,
    brief: RadarBrief,
    chars_per_second: float,
    caption: str | None = None,
    today: date | None = None,
) -> list[str]:
    """Onde o roteiro vai contra um PADRÃO do resumo, no que o código sabe medir. Indícios (`hint`) e o que
    não dá para medir no texto não geram alerta (`unmeasured_patterns` diz o que ficou sem conferência)."""
    warnings: list[str] = []
    if today is not None:
        age = (today - brief.generated_at.date()).days
        if age > MAX_AGE_DAYS:
            made = f"{brief.generated_at:%d/%m/%Y}"
            warnings.append(f"radar: resumo de {made} ({age} dias); gere outro no reels-radar")
    if brief.analysed < MIN_ANALYSED:
        warnings.append(
            f"radar: resumo com só {brief.analysed} Reels lidos (abaixo de {MIN_ANALYSED}): os padrões são "
            "hipótese, não base"
        )
    for g in brief.patterns():
        result = _measured(g.trait, scenes, brief, chars_per_second, caption)
        if result is None:
            continue
        has, detail = result
        if has != (g.advice == "use"):
            verb = "anda com mais" if g.advice == "use" else "anda com menos"
            state = "não tem" if g.advice == "use" else "tem"
            warnings.append(
                f"radar ({brief.niche}, {brief.analysed} Reels): {g.trait} {verb} {brief.measure_label()} "
                f"({_rates(g)}) e o roteiro {state}: {detail}"
            )
    return warnings


def unmeasured_patterns(
    scenes: ScenesManifest, brief: RadarBrief, chars_per_second: float, caption: str | None = None
) -> list[str]:
    """Padrões do resumo que o código não sabe conferir no texto: ficam para a prévia e a revisão humana."""
    return [
        g.trait
        for g in brief.patterns()
        if _measured(g.trait, scenes, brief, chars_per_second, caption) is None
    ]
