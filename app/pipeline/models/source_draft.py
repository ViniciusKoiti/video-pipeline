from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models.source_kind import SourceKind


@dataclass(frozen=True)
class SourceDraft:
    """O que o dono informa sobre a fonte antes de ela ter id."""

    title: str
    kind: SourceKind
    url: str | None = None  # None na fonte declarada
    authors: tuple[str, ...] = ()
    interested: bool = False
    notes: str = ""
