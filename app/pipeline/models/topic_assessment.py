from __future__ import annotations

from app.pipeline.models.model import Model
from app.pipeline.models.topic_kind import TopicKind


class TopicAssessment(Model):
    """Leitura do tema — produzida pelo adapter de texto (etapa 27) ou informada à mão."""

    kind: TopicKind
    period_year: int | None = None  # ano central do evento, se histórico
    rationale: str = ""
