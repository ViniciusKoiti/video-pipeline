from __future__ import annotations

from pathlib import Path

from pydantic import Field

from app.settings.models._settings_model import _Model
from app.settings.models._settings_value_default_delivery import _default_delivery
from app.settings.models.delivery_params import DeliveryParams


class ChatterboxSettings(_Model):
    """Voz clonada local (ADR 016, proposta). O ambiente do modelo e a gravação de referência vêm do .env."""

    python: Path | None = None  # CHATTERBOX_PYTHON: o Python do ambiente em que o modelo está instalado
    reference: Path | None = None  # CHATTERBOX_REFERENCE: gravação da voz a clonar (dado pessoal)
    model: str = "v3"
    language_ids: dict[str, str] = Field(default_factory=lambda: {"pt-BR": "pt", "en": "en"})
    num_threads: int = Field(default=12, gt=0)
    chars_per_second: float = Field(default=14.0, gt=0)
    pause_ms: int = Field(default=400, ge=0)  # silêncio no lugar de cada `<short pause>` (ADR 015)
    delivery: dict[str, DeliveryParams] = Field(default_factory=_default_delivery)  # por entrega (ADR 022)
