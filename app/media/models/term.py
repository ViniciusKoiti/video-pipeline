from __future__ import annotations

from pydantic import Field, field_validator

from app.media.models._pronunciation_model import _Model


class Term(_Model):
    escrita: str = Field(min_length=1)  # como está na narração
    fala: str = Field(min_length=1)  # como a voz deve ler
    # fonemas IPA da tabela do idioma, para a voz que aceita `<phoneme>` (Azure); as outras leem a `fala`
    ipa: str | None = Field(default=None, min_length=1)

    @field_validator("escrita", "fala", "ipa")
    @classmethod
    def _no_tags(cls, value: str | None) -> str | None:
        if value is not None and any(char in value for char in "<>\"&"):
            raise ValueError("sem marcas <…>, aspas nem & no glossário: as pausas ficam na narração")
        return value
