from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Radar(BaseModel):
    # O contrato é do reels-radar e pode ganhar campos: o que não é lido aqui é ignorado.
    model_config = ConfigDict(extra="ignore", frozen=True, populate_by_name=True)
