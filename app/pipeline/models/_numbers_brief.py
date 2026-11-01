from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Brief(BaseModel):
    # O contrato é da skill `analise-de-formato` e pode ganhar campos: o que não é lido aqui é ignorado.
    model_config = ConfigDict(extra="ignore", frozen=True, populate_by_name=True)
