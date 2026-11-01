from __future__ import annotations

from app.pipeline.models._affiliate_model import _Model
from app.pipeline.models.book import Book


class BookList(_Model):
    livros: list[Book]
