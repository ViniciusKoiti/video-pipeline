from __future__ import annotations

from pydantic import Field, field_validator

from app.media.models._pronunciation_model import _Model


class Term(_Model):
    escrita: str = Field(min_length=1)  # como está na narração
    fala: str = Field(min_length=1)  # como a voz deve ler

    @field_validator("escrita", "fala")
    @classmethod
    def _no_tags(cls, value: str) -> str:
        if "<" in value or ">" in value:
            raise ValueError("sem marcas <…> no glossário: as pausas ficam na narração")
        return value
