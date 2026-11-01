from __future__ import annotations

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class DocumentHeader(Model):
    """Cabeçalho da página recriada; o texto real da página é só o trecho citado (ADR 011)."""

    title: NonEmpty
    issuer: str = ""
    date: str = ""
