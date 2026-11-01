from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from app.pipeline.models._schemas_shot import _Shot
from app.pipeline.models._schemas_types import KEYWORD_MAX_WORDS, NonEmpty, _fold


class KeywordShot(_Shot):
    """Frase-chave da narração na tela (KineticHeadline). Cópia literal da narração da cena, que já tem
    as suas claims; por isso o plano não exige claims próprias (ADR 011)."""

    kind: Literal["keyword"] = "keyword"
    text: NonEmpty
    highlight: str = ""  # trecho do `text` em destaque

    @model_validator(mode="after")
    def _short_and_consistent(self) -> Self:
        if len(self.text.split()) > KEYWORD_MAX_WORDS:
            raise ValueError(f"frase na tela com mais de {KEYWORD_MAX_WORDS} palavras: {self.text!r}")
        if self.highlight and _fold(self.highlight) not in _fold(self.text):
            raise ValueError(f"destaque {self.highlight!r} fora da frase {self.text!r}")
        return self
