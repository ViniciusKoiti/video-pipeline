from __future__ import annotations

from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.model import Model


class ReceiptTotal(Model):
    label: str = ""  # vazio: "Total" no idioma do episódio
    value: NonEmpty  # a soma das linhas, escrita pelo roteirista; o `vp check` refaz (ADR 028, decisão 2)
    anchor: NonEmpty  # o total entra quando é dito
