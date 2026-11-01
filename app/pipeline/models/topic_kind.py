from __future__ import annotations

from enum import StrEnum


class TopicKind(StrEnum):
    HISTORICAL_EVENT = "historical_event"
    CONCEPT = "concept"
    UNCLEAR = "unclear"
