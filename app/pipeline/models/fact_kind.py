from __future__ import annotations

from enum import StrEnum


class FactKind(StrEnum):
    """O que o fato faz pela história. `context` explica; os outros prendem o público."""

    NUMBER = "number"  # valor, preço, quantidade, escala
    CONFLICT = "conflict"  # disputa, risco, quem perdeu
    TURNING_POINT = "turning_point"  # decisão ou evento que mudou o rumo
    MECHANISM = "mechanism"  # como o dinheiro ou o poder foi feito
    CURIOSITY = "curiosity"  # detalhe contraintuitivo ou humano
    IMPACT_TODAY = "impact_today"  # o que o público usa ou paga hoje por causa do personagem
    RULE = "rule"  # lei, tarifa, subsídio ou decisão de Estado que mudou o negócio
    CONTEXT = "context"  # pano de fundo necessário
