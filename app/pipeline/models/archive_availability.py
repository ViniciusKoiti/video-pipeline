from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models.skipped_archive import SkippedArchive
from app.providers.archives.base import ArchiveProvider


@dataclass(frozen=True)
class ArchiveAvailability:
    """Os bancos da cascata usáveis agora, na ordem do `providers.toml`, e os que foram pulados."""

    archives: tuple[ArchiveProvider, ...]
    skipped: tuple[SkippedArchive, ...] = ()
