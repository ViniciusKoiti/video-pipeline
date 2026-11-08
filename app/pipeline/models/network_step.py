from __future__ import annotations

from typing import Self

from pydantic import model_validator

from app.pipeline.models._schemas_types import NodeId, NonEmpty
from app.pipeline.models.model import Model


class NetworkStep(Model):
    anchor: NonEmpty  # trecho da narração em que o passo entra, depois da âncora do plano
    nodes: list[NodeId] = []  # nós que entram
    highlight: list[NodeId] = []  # nós acesos (e as arestas entre eles); o resto esmaece

    @model_validator(mode="after")
    def _does_something(self) -> Self:
        if not self.nodes and not self.highlight:
            raise ValueError(f"passo {self.anchor!r} sem nós novos nem destaque")
        return self
