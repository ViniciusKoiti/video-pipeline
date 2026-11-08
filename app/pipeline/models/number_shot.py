from __future__ import annotations

from typing import Literal

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import NonEmpty


class NumberShot(_FactualShot):
    kind: Literal["number"] = "number"
    value: NonEmpty  # como aparece na tela: "1.500", "US$ 4,2 bi"
    label: NonEmpty
