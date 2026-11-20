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
from datetime import date

from app.media.narration import strip_pauses, timeline_length
from app.pipeline.constants.radar_constants import RadarConstants
from app.pipeline.models._radar_radar import _Radar as _Radar
from app.pipeline.models.radar_brief import RadarBrief as RadarBrief
from app.pipeline.models.radar_guidance import RadarGuidance as RadarGuidance
from app.pipeline.models.radar_purposes import RadarPurposes as RadarPurposes
from app.pipeline.schemas import ScenesManifest

# `measure` do resumo -> como o alerta a chama. Resumo antigo não tem o campo, e a medida fica desconhecida.


# tipo do radar -> objetivo do roteiro (ADR 019)


def brief_summary(brief: RadarBrief) -> str:
    return (
        (
        f'{RadarConstants.BRIEF_FILE}: nicho {brief.niche}, {brief.analysed}'
        f' Reels lidos, de {brief.generated_at:%d/%m/%Y}; {len(brief.patterns())}'
        f' padrão(ões) e {len(brief.hints())} indício(s) de forma; '
    )
        + (
            "medida não informada (resumo antigo)"
            if brief.measure is None
            else f"medida: {brief.measure_label()}"
        )
        + (_purposes_summary(brief.purposes) if brief.purposes else "")
    )


def _purposes_summary(purposes: RadarPurposes) -> str:
    names = {"news": "notícia", "explain": "explicação", "opinion": "opinião", "none": "sem sinal"}
    counts = ", ".join(f"{names.get(kind, kind)} {n}" for kind, n in purposes.main_purposes.items())
    return f"; tipos lidos em {purposes.read} Reels ({counts})"


def opening_sentence(scenes: ScenesManifest) -> str:
    """A primeira frase falada do vídeo, sem as marcas de pausa."""
    text = strip_pauses(scenes.scenes[0].narration).strip()
    return RadarConstants._SENTENCE_END.split(text, maxsplit=1)[0]


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
    if trait in RadarConstants.PURPOSE_KINDS:
        if scenes.objective is None:
            return None  # sem objetivo declarado não há o que comparar; o `vp check` já avisa disso
        objectives = scenes.objective.kinds
        return RadarConstants.PURPOSE_KINDS[
            trait
        ] in objectives, f"o objetivo declarado é {' + '.join(objectives)}"
    if trait == "long_video" and (limit := brief.threshold("long_video_above_s")) is not None:
        seconds = sum(timeline_length(s.narration) for s in scenes.scenes) / chars_per_second
        return seconds > limit, f"o roteiro tem ~{seconds:.0f} s e o corte é {limit:.0f} s"
    if trait == "addresses_viewer" and scenes.language in RadarConstants._VIEWER:
        found = re.search(RadarConstants._VIEWER[scenes.language], opening, re.IGNORECASE) is not None
        return found, f"abertura: {opening!r}"
    if trait == "opens_question":
        return opening.rstrip().endswith("?"), f"abertura: {opening!r}"
    if trait == "long_opening" and (limit := brief.threshold("long_opening_above_words")) is not None:
        words = len(opening.split())
        return words > limit, f"a abertura tem {words} palavras e o corte é {limit:.0f}"
    if trait == "screen_alert":
        kinds = [shot.kind for shot in scenes.scenes[0].shots[:RadarConstants.OPENING_SHOTS]]
        return "keyword" in kinds, f"primeiros planos: {', '.join(kinds) or 'nenhum'}"
    if caption is not None:
        first_line = caption.strip().splitlines()[0] if caption.strip() else ""
        if trait == "has_emoji":
            return RadarConstants._EMOJI.search(
                first_line
            ) is not None, f"primeira linha da legenda: {first_line!r}"
        if trait == "ask_comment":
            return RadarConstants._ASKS_COMMENT.search(caption) is not None, "legenda do post"
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
        if age > RadarConstants.MAX_AGE_DAYS:
            made = f"{brief.generated_at:%d/%m/%Y}"
            warnings.append(f"radar: resumo de {made} ({age} dias); gere outro no reels-radar")
    if brief.analysed < RadarConstants.MIN_ANALYSED:
        warnings.append(
            f"radar: resumo com só {brief.analysed} Reels lidos (abaixo de "
            f"{RadarConstants.MIN_ANALYSED}): os padrões são hipótese, não base"
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
                f"radar ({brief.niche}, {brief.analysed} Reels): {g.trait} {verb} "
                f"{brief.measure_label()} ({_rates(g)}) e o roteiro {state}: {detail}"
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
