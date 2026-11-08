from __future__ import annotations

from pydantic import Field

from app.pipeline.models._schemas_shot import _Shot
from app.pipeline.models.claim import Claim


class _FactualShot(_Shot):
    # Número, data, citação ou cargo na tela é afirmação: fora do regime `entretenimento`, o `ScenesManifest`
    # exige a claim (ADR 008 e 056); aqui a lista só não pode faltar.
    claims: list[Claim] = Field(default_factory=list)
