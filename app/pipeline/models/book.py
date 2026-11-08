from __future__ import annotations

from pydantic import Field

from app.pipeline.models._affiliate_model import _Model


class Book(_Model):
    titulo: str = Field(min_length=1)
    autor: str = Field(min_length=1)
    link: str | None = None  # link do produto copiado da SiteStripe; sem ele, uma busca
    busca: str | None = None  # termos da busca; padrão: título e autor
