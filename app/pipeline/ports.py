"""Portas internas do pipeline e o `Context` recebido pelas etapas (ADR 006).

As etapas dependem só destes Protocols; quem monta as implementações é `app.bootstrap`.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, TypeVar

from pydantic import BaseModel

from app.pipeline.schemas import ReviewEntry, ReviewLog
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


class ManifestStore(Protocol):
    """Manifestos de um episódio. Hoje JSON em `data/episodes/<id>/`; SQLite só se virar obstáculo (§11)."""

    def path(self, episode_id: str, name: str) -> Path: ...

    def exists(self, episode_id: str, name: str) -> bool: ...

    def read(self, episode_id: str, name: str, model: type[M]) -> M: ...  # ausente → ManifestNotFound

    def write(self, episode_id: str, name: str, manifest: BaseModel) -> None: ...


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
    @property
    def render(self) -> RenderEngine: ...
