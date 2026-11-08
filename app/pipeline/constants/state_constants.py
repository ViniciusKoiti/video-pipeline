"""Constantes de state; dados fixos sem I/O."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

from app.pipeline.schemas import Status

if TYPE_CHECKING:
    from collections.abc import Mapping


class StateConstants:
    MANIFEST: Final[str] = "manifest.json"
    TRANSITIONS: Final[Mapping[Status, frozenset[Status]]] = MappingProxyType(
        {
            Status.PENDING: frozenset((Status.RUNNING,)),
            # RUNNING -> RUNNING: processo interrompido; quem tem o lock do episódio retoma (RF2)
            Status.RUNNING: frozenset((Status.RUNNING, Status.NEEDS_REVIEW, Status.COMPLETED, Status.FAILED)),
            Status.NEEDS_REVIEW: frozenset((Status.APPROVED, Status.RUNNING)),
            Status.APPROVED: frozenset((Status.COMPLETED,)),
            Status.COMPLETED: frozenset((Status.RUNNING,)),
            Status.FAILED: frozenset((Status.RUNNING,)),
        }
    )
