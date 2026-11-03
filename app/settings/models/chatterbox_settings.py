from __future__ import annotations

import re
from pathlib import Path

from pydantic import Field, model_validator

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
    references: dict[str, dict[str, Path]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_references(self) -> ChatterboxSettings:
        for language, entries in self.references.items():
            if language not in self.language_ids or not re.fullmatch(r"[A-Za-z0-9-]+", language):
                raise ValueError(f"idioma de referência desconhecido: {language}")
            for delivery, path in entries.items():
                if delivery not in self.delivery or not re.fullmatch(r"[A-Za-z0-9-]+", delivery):
                    raise ValueError(f"entrega de referência desconhecida: {delivery}")
                if path.suffix.lower() != ".wav":
                    raise ValueError(f"referência {language}/{delivery}: use o WAV convertido")
        return self
