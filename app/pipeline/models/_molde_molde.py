from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Molde(BaseModel):
    # O contrato é da skill e pode ganhar campos: o que não é lido aqui é ignorado.
    model_config = ConfigDict(extra="ignore", frozen=True)
