"""Portas internas do pipeline e o `Context` recebido pelas etapas (ADR 006).

As etapas dependem só destes Protocols; quem monta as implementações é `app.bootstrap`.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Protocol, TypeVar

from pydantic import BaseModel

from app.pipeline.schemas import EpisodeFormat, ReviewEntry, ReviewLog
from app.providers.alignment.base import SubtitleAligner
from app.providers.archives.base import ArchiveProvider
from app.providers.image_gen.base import ImageGenProvider
from app.providers.text.base import TextProvider
from app.providers.tts.base import TTSProvider
from app.render.base import RenderEngine
from app.settings import Settings

M = TypeVar("M", bound=BaseModel)


class ManifestNotFound(LookupError):
    pass


class ImmutableManifest(PermissionError):
    """§2.6: arquivo aprovado não é sobrescrito pelo código; reabrir é explícito (vp reopen)."""


class EpisodeLocked(RuntimeError):
    """Outra execução já está trabalhando neste episódio (uma de cada vez, §3)."""


def is_approved_json(raw: str) -> bool:
    """Manifesto com `review_status` de topo aprovado (ex.: ativo): nenhum armazenamento o sobrescreve."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(data, dict) and data.get("review_status") in ("approved", "completed")


class ManifestStore(Protocol):
    """Manifestos de um episódio. Hoje JSON em `data/episodes/<id>/`; SQLite só se virar obstáculo (§11)."""

    def path(self, episode_id: str, name: str) -> Path: ...

    def exists(self, episode_id: str, name: str) -> bool: ...

    def read(self, episode_id: str, name: str, model: type[M]) -> M: ...  # ausente → ManifestNotFound

    # Arquivo aprovado → ImmutableManifest (§2.6).
    def write(self, episode_id: str, name: str, manifest: BaseModel) -> None: ...

    def lock(self, episode_id: str) -> AbstractContextManager[None]: ...  # ocupado → EpisodeLocked


class ReviewGate(Protocol):
    """Decisões humanas (§2.5). Hoje `review.json` + `vp approve`; galeria/web depois."""

    def record(self, episode_id: str, entry: ReviewEntry) -> None: ...  # só acrescenta

    def log(self, episode_id: str) -> ReviewLog: ...


class Context(Protocol):
    """Tudo o que uma etapa pode usar, passado explicitamente (sem estado global)."""

    @property
    def settings(self) -> Settings: ...
    @property
    def store(self) -> ManifestStore: ...
    @property
    def review(self) -> ReviewGate: ...
    @property
    def text(self) -> TextProvider: ...
    @property
    def tts(self) -> TTSProvider: ...
    @property
    def image_gen(self) -> ImageGenProvider: ...
    @property
    def archives(self) -> Sequence[ArchiveProvider]: ...  # na ordem da cascata
    @property
    def aligner(self) -> SubtitleAligner: ...
    def renderer(self, episode_format: EpisodeFormat) -> RenderEngine: ...  # motor do formato (ADR 001)
