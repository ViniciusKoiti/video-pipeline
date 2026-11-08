from __future__ import annotations

from pydantic import Field

from app.pipeline.models._schemas_shot import _Shot
from app.pipeline.models.claim import Claim


class _FactualShot(_Shot):
    claims: list[Claim] = Field(min_length=1)  # número, data, citação ou cargo na tela é afirmação
