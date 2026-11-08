from __future__ import annotations

from typing import Literal

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import NonEmpty


class LowerThirdShot(_FactualShot):
    kind: Literal["lower_third"] = "lower_third"  # tarja de nome e cargo
    name: NonEmpty
    role: NonEmpty
