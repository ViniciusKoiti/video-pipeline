from __future__ import annotations

from typing import Literal

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import NonEmpty


class StampShot(_FactualShot):
    kind: Literal["stamp"] = "stamp"  # carimbo de data e lugar
    date: NonEmpty
    place: str = ""
