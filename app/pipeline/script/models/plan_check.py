"""Um plano em conferência no `vp check`, com o que as regras por plano precisam saber em volta (ADR 064)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.pipeline.schemas import Language, Shot


@dataclass(frozen=True)
class PlanCheck:
    """`over_media`: foto ou B-roll da cena já na tela, e o plano vai por cima dela (tarja, número, carimbo).
    `explains`: o vídeo declara `explicar` (ou não declara objetivo); só então vale conta na tela (ADR 020).
    """

    scene_id: str
    shot: Shot
    ms: float
    over_media: bool
    language: Language
    explains: bool
    region_codes: frozenset[str] | None
    excerpts: Mapping[str, str]
