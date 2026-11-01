from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models._schemas_shot import _Shot
from app.pipeline.models._schemas_types import NonEmpty, _fold


class HookShot(_Shot):
    """Gancho (`HookCard` do kit), legível já no primeiro quadro: só no primeiro plano do vídeo (ADR 028). O
    texto é cópia literal da narração, como o `keyword`; número, data ou nome nele pede claims (§2.2)."""

    kind: Literal["hook"] = "hook"
    text: NonEmpty
    highlight: str = ""  # trecho do `text` em destaque

    @model_validator(mode="after")
    def _short_and_sourced(self) -> Self:
        if len(self.text.split()) > SchemasConstants.HOOK_MAX_WORDS:
            raise ValueError(f"gancho com mais de {SchemasConstants.HOOK_MAX_WORDS} palavras: {self.text!r}")
        if self.highlight and _fold(self.highlight) not in _fold(self.text):
            raise ValueError(f"destaque {self.highlight!r} fora do gancho {self.text!r}")
        if any(c.isdigit() for c in self.text) and not self.claims:
            raise ValueError(f"gancho com número precisa de claims (§2.2): {self.text!r}")
        return self
