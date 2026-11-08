"""Constantes de format_decision; dados fixos sem I/O."""

from __future__ import annotations

from typing import Final

from app.pipeline.schemas import VisualNeed


class FormatDecisionConstants:
    # publicado até 1930 = domínio público nos EUA (§8)
    PUBLIC_DOMAIN_CUTOFF_YEAR: Final[int] = 1930
    # a partir desta fração de cenas gráficas, o vídeo é um explicativo
    EXPLAINER_GRAPHIC_SHARE: Final[float] = 0.6
    # visual gerado a partir de dados
    GRAPHIC_NEEDS: Final = frozenset((VisualNeed.MAP_OR_GRAPHIC,))
    PHOTO_NEEDS: Final = frozenset((VisualNeed.HISTORICAL_EXACT, VisualNeed.CONTEXTUAL_STOCK))
