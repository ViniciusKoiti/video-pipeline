from __future__ import annotations

from datetime import date

from app.pipeline.models._schemas_types import NonEmpty, RequestKind
from app.pipeline.models.model import Model


class AudienceRequest(Model):
    """Pedido visto nos comentários, resumido e sem dado pessoal (D6)."""

    date: date
    kind: RequestKind
    summary: NonEmpty
