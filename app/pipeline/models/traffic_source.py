from __future__ import annotations

from app.pipeline.models._schemas_types import NonEmpty, Percent
from app.pipeline.models.model import Model


class TrafficSource(Model):
    """Uma origem de tráfego, com o rótulo do Studio ("Navegação", "Sugeridos", "Pesquisa do YouTube")."""

    name: NonEmpty
    percent: Percent
