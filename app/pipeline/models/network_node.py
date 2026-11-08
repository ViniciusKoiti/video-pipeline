from __future__ import annotations

from typing import Literal

from app.pipeline.models._schemas_types import NodeId, NonEmpty
from app.pipeline.models.model import Model


class NetworkNode(Model):
    id: NodeId
    label: NonEmpty  # nome da pessoa ou instituição
    role: str = ""
    # O ícone sai do tipo, no template: o roteiro não escolhe ícone, cor nem logo.
    kind: Literal["person", "family", "company", "bank", "government", "other"]
