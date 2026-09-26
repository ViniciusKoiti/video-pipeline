"""`ManifestStore` em arquivos JSON: `data/episodes/<id>/<nome>` (§3, §11: banco só se virar obstáculo)."""

from __future__ import annotations

import fcntl
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.pipeline.ports import EpisodeLocked, ImmutableManifest, ManifestNotFound, is_approved_json

M = TypeVar("M", bound=BaseModel)


class JsonFileStore:
    def __init__(self, root: Path) -> None:
        self._root = root

    def path(self, episode_id: str, name: str) -> Path:
        return self._root / episode_id / name

    def exists(self, episode_id: str, name: str) -> bool:
        return self.path(episode_id, name).is_file()

    def read(self, episode_id: str, name: str, model: type[M]) -> M:
        try:
            return model.model_validate_json(self.path(episode_id, name).read_text())
        except FileNotFoundError:
            raise ManifestNotFound(f"{episode_id}/{name}") from None

    def write(self, episode_id: str, name: str, manifest: BaseModel) -> None:
        path = self.path(episode_id, name)
        if path.is_file() and is_approved_json(path.read_text()):
            raise ImmutableManifest(f"{episode_id}/{name} está aprovado; o código não o sobrescreve (§2.6)")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.tmp")
        tmp.write_text(manifest.model_dump_json(indent=2) + "\n")
        tmp.replace(path)  # atômico: um manifesto nunca fica pela metade

    @contextmanager
    def lock(self, episode_id: str) -> Iterator[None]:
        path = self.path(episode_id, ".lock")
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise EpisodeLocked(f"{episode_id} já está em uso por outra execução") from None
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
