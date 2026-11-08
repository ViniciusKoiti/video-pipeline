from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models.asset import Asset
from app.pipeline.models.intake_action import IntakeAction


@dataclass(frozen=True)
class IntakeResult:
    asset: Asset  # o ativo como está em `assets/<id>.json` depois da entrada
    action: IntakeAction
