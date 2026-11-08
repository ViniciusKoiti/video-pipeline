from __future__ import annotations

from pydantic import Field

from app.pipeline.constants.medicao_constants import MedicaoConstants
from app.pipeline.models.model import Model


class Numero(Model):
    """Um número dito ou mostrado, e de onde ele vem."""

    valor: float
    trechos: list[str] = []  # trechos literais do arquivo de resultado
    medidos: list[float] = []  # os valores medidos que o número resume; vazio = os números dos trechos
    tolerancia: float = Field(default=MedicaoConstants.DEFAULT_TOLERANCE, ge=0)  # relativa ao medido
    fator: float = 1.0  # unidade: medido × fator = a unidade dita (ms → s é 0.001)
    cenas: list[str] | None = None  # só vale nessas cenas; None = em qualquer cena
    nota: str | None = None  # obrigatória sem trechos: por que não é uma medida (nome, contagem)
