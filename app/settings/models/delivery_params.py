from __future__ import annotations

from pydantic import Field

from app.settings.models._settings_model import _Model


class DeliveryParams(_Model):
    """Controles de expressividade do Chatterbox para uma entrega (ADR 022)."""

    exaggeration: float = Field(default=0.5, ge=0, le=2)  # ênfase; o modelo usa 0,5 por padrão
    cfg_weight: float = Field(default=0.5, ge=0, le=1)  # quanto menor, mais vivo e rápido
