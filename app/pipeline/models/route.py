from __future__ import annotations

from app.pipeline.models._schemas_from_to import _FromTo


class Route(_FromTo):
    """Rota entre dois lugares do mapa, pelos nomes em `places`."""
