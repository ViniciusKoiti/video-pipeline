"""O que as regras de episódio do `vp check` recebem: o episódio já lido e os parâmetros (ADR 064)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from app.pipeline.ports import ManifestStore
from app.pipeline.schemas import FactsManifest, MusicCatalog, ScenesManifest, Shot, SourcesManifest


@dataclass
class CheckedEpisode:
    """`planned` é preenchido pela regra das cenas (cada plano com a duração estimada) e lido pelas
    citações."""

    store: ManifestStore
    episode_id: str
    sources: SourcesManifest | None
    facts: FactsManifest | None
    scenes: ScenesManifest | None
    excerpts: Mapping[str, str]
    region_codes: frozenset[str] | None
    chars_per_second: float
    today: date | None
    music_catalog: MusicCatalog | None
    measure: Callable[[Path], float] | None
    final_voice: str | None
    planned: list[tuple[str, Shot, float]] = field(default_factory=list)
