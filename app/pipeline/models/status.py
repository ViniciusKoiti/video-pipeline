from __future__ import annotations

from enum import StrEnum


class Status(StrEnum):
    """Estados de etapa, cena e ativo (§5)."""

    PENDING = "pending"
    RUNNING = "running"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"
