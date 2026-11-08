from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Sample(BaseModel):
    """Um instante por plano: uma linha da folha de quadros."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str  # "S01#2": cena e posição do plano na cena
    kind: str
    at_ms: int
