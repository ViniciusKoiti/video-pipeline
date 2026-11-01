from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models.timeline_event import TimelineEvent


class TimelineShot(_FactualShot):
    kind: Literal["timeline"] = "timeline"
    events: list[TimelineEvent] = Field(min_length=2)
