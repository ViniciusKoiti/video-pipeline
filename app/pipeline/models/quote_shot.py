from __future__ import annotations

from typing import Literal, Self

from pydantic import model_validator

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import NonEmpty
from app.pipeline.models.document_header import DocumentHeader


class QuoteShot(_FactualShot):
    kind: Literal["quote"] = "quote"  # citação ou manchete recriada como tipografia, nunca print (§8)
    text: NonEmpty  # literal num dos trechos citados (`vp check`, ADR 011)
    attribution: NonEmpty
    style: Literal["quote", "headline", "document"] = "quote"
    document: DocumentHeader | None = None  # obrigatório em `document`; opcional em `headline`
    variant: Literal["report", "newspaper", "letter"] = "report"  # só `document`

    @model_validator(mode="after")
    def _document_header(self) -> Self:
        if self.style == "document" and self.document is None:
            raise ValueError("citação em página de documento precisa do cabeçalho (document)")
        if self.style == "quote" and self.document is not None:
            raise ValueError("document só vale nos estilos document e headline")
        return self
