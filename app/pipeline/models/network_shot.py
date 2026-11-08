from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_factual_shot import _FactualShot
from app.pipeline.models._schemas_types import NodeId, _unique
from app.pipeline.models.network_edge import NetworkEdge
from app.pipeline.models.network_node import NetworkNode
from app.pipeline.models.network_step import NetworkStep


class NetworkShot(_FactualShot):
    """Rede que cresce no ritmo da narração enquanto a câmera se afasta (ExpandingNetwork)."""

    kind: Literal["network"] = "network"
    root: NodeId
    nodes: list[NetworkNode] = Field(min_length=2)
    edges: list[NetworkEdge] = Field(min_length=1)
    steps: list[NetworkStep] = Field(min_length=1)
    layout: Literal["radial", "layered"] = "radial"

    @model_validator(mode="after")
    def _consistent_graph(self) -> Self:
        ids = [n.id for n in self.nodes]
        _unique(ids, "nós da rede")
        _unique([f"{e.from_}->{e.to}" for e in self.edges], "arestas da rede")
        known = set(ids)
        if self.root not in known:
            raise ValueError(f"raiz {self.root!r} não está entre os nós")
        referenced = {self.root} | {x for e in self.edges for x in (e.from_, e.to)}
        referenced |= {x for s in self.steps for x in s.nodes + s.highlight}
        unknown = sorted(referenced - known)
        if unknown:
            raise ValueError(f"nós inexistentes na rede: {', '.join(unknown)}")
        entering = [x for s in self.steps for x in s.nodes]
        _unique(entering, "nós que entram nos passos")
        if self.root in entering:
            raise ValueError("a raiz já abre o plano; não entra de novo num passo")
        never = sorted(known - set(entering) - {self.root})
        if never:
            raise ValueError(f"nós que nunca entram na rede: {', '.join(never)}")
        return self
