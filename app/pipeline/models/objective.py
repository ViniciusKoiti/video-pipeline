from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import _OBJECTIVE_FIELDS, NonEmpty, ObjectiveKind, _unique
from app.pipeline.models.model import Model


class Objective(Model):
    """O que o vídeo se propõe a fazer, declarado antes do roteiro (ADR 019).

    `kinds` traz de um a três tipos, na ordem em que aparecem no vídeo; o primeiro é o principal e manda na
    estrutura. Um vídeo pode só explicar, ou noticiar, explicar e opinar no fim: depende da pauta.

    - `noticiar`: conta um fato novo; `event_date` diz quando ele aconteceu.
    - `explicar`: responde a uma pergunta; `question` é a pergunta, e o vídeo a responde.
    - `opinar`: defende uma tese, dita como opinião; `thesis` e de quem ela é (`thesis_by`). A tese vem do
      dono, nunca do agente; os fatos que a apoiam seguem com fonte (§2.2)."""

    kinds: list[ObjectiveKind] = Field(min_length=1, max_length=3)
    promise: NonEmpty  # uma frase: o que a pessoa sabe, entende ou pensa depois de assistir
    event_date: date | None = None
    question: NonEmpty | None = None
    thesis: NonEmpty | None = None
    thesis_by: NonEmpty | None = None

    @property
    def main(self) -> ObjectiveKind:
        return self.kinds[0]

    @model_validator(mode="after")
    def _fields_match_kinds(self) -> Self:
        _unique(self.kinds, "tipos de objetivo")
        for kind, names in _OBJECTIVE_FIELDS.items():
            given = [name for name in names if getattr(self, name) is not None]
            if kind in self.kinds and len(given) < len(names):
                missing = ", ".join(name for name in names if name not in given)
                raise ValueError(f"objetivo {kind} precisa de {missing}")
            if kind not in self.kinds and given:
                raise ValueError(f"{', '.join(given)} só existe com o objetivo {kind}")
        if self.question is not None and not self.question.rstrip().endswith("?"):
            raise ValueError("question é uma pergunta: termina com '?'")
        return self
