from __future__ import annotations

from app.media.models._pronunciation_model import _Model
from app.media.models.term import Term


class Glossary(_Model):
    termos: list[Term] = []
