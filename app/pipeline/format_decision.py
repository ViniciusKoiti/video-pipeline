"""Tomador de decisão da modalidade do vídeo (ADR 001).

Recomenda o formato do episódio — e, pelo mapa de `config/providers.toml`, o motor de render — em dois
momentos: pelo tema (no `vp new`, a partir da avaliação do LLM local) e pelas cenas (depois do
`vp scenes`, por regras sobre os `visual_need`). Só recomenda: o formato vale depois que um humano
confirma ou troca no `review.json` (`step: format`, §2.5).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import AwareDatetime, Field

from app.pipeline.schemas import (
    Decision,
    EpisodeFormat,
    Model,
    ReviewLog,
    SceneId,
    ScenesManifest,
    Step,
    VisualNeed,
)

PUBLIC_DOMAIN_CUTOFF_YEAR = 1930  # publicado até 1930 = domínio público nos EUA (§8)
EXPLAINER_GRAPHIC_SHARE = 0.6  # a partir desta fração de cenas gráficas, o vídeo é um explicativo
GRAPHIC_NEEDS = frozenset({VisualNeed.MAP_OR_GRAPHIC})  # visual gerado a partir de dados
PHOTO_NEEDS = frozenset({VisualNeed.HISTORICAL_EXACT, VisualNeed.CONTEXTUAL_STOCK})


class TopicKind(StrEnum):
    HISTORICAL_EVENT = "historical_event"
    CONCEPT = "concept"
    UNCLEAR = "unclear"


class TopicAssessment(Model):
    """Leitura do tema — produzida pelo adapter de texto (etapa 27) ou informada à mão."""

    kind: TopicKind
    period_year: int | None = None  # ano central do evento, se histórico
    rationale: str = ""


class FormatDecision(Model):
    stage: Literal["topic", "scenes"]
    recommended: EpisodeFormat
    scores: dict[EpisodeFormat, float]
    reasons: list[str] = Field(min_length=1)
    graphic_scenes_as_assets: list[SceneId] = []  # cenas para o caminho "gráfico como ativo" (etapa #42)
    input_hash: str
    decided_at: AwareDatetime


class FormatNotConfirmed(LookupError):
    pass


def _hash(payload: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def _decision(
    stage: Literal["topic", "scenes"],
    documentary: float,
    reasons: list[str],
    payload: object,
    now: datetime,
    graphic_assets: list[str] | None = None,
) -> FormatDecision:
    scores = {
        EpisodeFormat.ARCHIVAL_DOCUMENTARY: round(documentary, 2),
        EpisodeFormat.EXPLAINER: round(1 - documentary, 2),
    }
    recommended = (  # empate fica com o formato do MVP
        EpisodeFormat.EXPLAINER
        if scores[EpisodeFormat.EXPLAINER] > 0.5
        else EpisodeFormat.ARCHIVAL_DOCUMENTARY
    )
    return FormatDecision(
        stage=stage,
        recommended=recommended,
        scores=scores,
        reasons=reasons,
        graphic_scenes_as_assets=graphic_assets or [],
        input_hash=_hash(payload),
        decided_at=now,
    )


def decide_from_topic(topic: TopicAssessment, *, now: datetime) -> FormatDecision:
    """Primeira recomendação, no `vp new`, antes de existirem cenas."""
    if topic.kind is TopicKind.CONCEPT:
        return _decision(
            "topic",
            0.15,
            ["tema é explicação de conceito: o visual vem de dados (código, diagramas, gráficos)"],
            topic.model_dump(),
            now,
        )
    if topic.kind is TopicKind.UNCLEAR:
        return _decision(
            "topic",
            0.5,
            ["tema ambíguo: revisar à mão; na dúvida, o formato do MVP"],
            topic.model_dump(),
            now,
        )
    reasons = ["tema é evento histórico: fotos de arquivo sustentam a narrativa"]
    if topic.period_year is None:
        documentary = 0.7
        reasons.append("período não informado: disponibilidade de fotos em domínio público incerta")
    elif topic.period_year <= PUBLIC_DOMAIN_CUTOFF_YEAR:
        documentary = 0.9
        reasons.append(
            f"{topic.period_year} ≤ {PUBLIC_DOMAIN_CUTOFF_YEAR}: fotos publicadas até 1930 são "
            "domínio público nos EUA (§8)"
        )
    else:
        documentary = 0.45
        reasons.append(
            f"{topic.period_year} > {PUBLIC_DOMAIN_CUTOFF_YEAR}: fotos raramente em domínio público; "
            "risco de virar 100% ilustração, que o §1 manda evitar"
        )
    return _decision("topic", documentary, reasons, topic.model_dump(), now)


def decide_from_scenes(scenes: ScenesManifest, *, now: datetime) -> FormatDecision:
    """Revisão depois do `vp scenes`, com os `visual_need` reais."""
    needs = [scene.visual_need for scene in scenes.scenes]
    graphic = [s.id for s in scenes.scenes if s.visual_need in GRAPHIC_NEEDS]
    photos = sum(need in PHOTO_NEEDS for need in needs)
    share = len(graphic) / len(needs)
    reasons = [
        f"{photos} de {len(needs)} cenas pedem foto (historical_exact/contextual_stock)",
        f"{len(graphic)} de {len(needs)} cenas pedem gráfico (map_or_graphic): {share:.0%}",
    ]
    if share >= EXPLAINER_GRAPHIC_SHARE:
        reasons.append(f"≥ {EXPLAINER_GRAPHIC_SHARE:.0%} de cenas gráficas: o vídeo é um explicativo")
        return _decision("scenes", 1 - share, reasons, [n.value for n in needs], now)
    assets = graphic if graphic else None
    if graphic:
        reasons.append(
            "cenas gráficas minoritárias: gerar como clipe 'gráfico como ativo' (etapa #42), "
            "sem trocar de formato"
        )
    return _decision("scenes", min(1 - share, 0.95), reasons, [n.value for n in needs], now, assets)


def confirmed_format(decision: FormatDecision, review: ReviewLog) -> EpisodeFormat:
    """Formato em vigor: o recomendado se aprovado, ou o escolhido pelo humano (`choice`) na mesma decisão.
    Sem confirmação para este `input_hash` (a entrada mudou), não há formato em vigor."""
    entry = review.latest(Step.FORMAT)
    if entry is None or entry.input_hash != decision.input_hash:
        raise FormatNotConfirmed("modalidade ainda não confirmada para esta decisão (gate 1, §2.5)")
    if entry.choice is not None:
        return EpisodeFormat(entry.choice)
    if entry.decision is not Decision.APPROVED:
        raise FormatNotConfirmed(f"recomendação {decision.recommended} não aprovada: {entry.decision}")
    return decision.recommended
