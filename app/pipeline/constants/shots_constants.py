"""Constantes de shots; dados fixos sem I/O."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from app.pipeline.schemas import EpisodeFormat


class ShotsConstants:
    MIN_SHOT_MS: Final[int] = 1500
    TARGET_AVERAGE_MS: Final[Mapping[EpisodeFormat, tuple[int, int]]] = MappingProxyType(
        {EpisodeFormat.EXPLAINER: (2000, 4000), EpisodeFormat.ARCHIVAL_DOCUMENTARY: (4000, 6000)}
    )
