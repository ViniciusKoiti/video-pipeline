from __future__ import annotations

from app.pipeline.models._schemas_types import ExcerptId, NonEmpty
from app.pipeline.models.model import Model


class Evidence(Model):
    excerpt_id: ExcerptId
    quote: NonEmpty  # cópia literal do trecho ("..." marca corte); `vp check` confere no texto da fonte
