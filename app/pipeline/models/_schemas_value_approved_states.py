from __future__ import annotations

from app.pipeline.models.status import Status

APPROVED_STATES = frozenset({Status.APPROVED, Status.COMPLETED})
