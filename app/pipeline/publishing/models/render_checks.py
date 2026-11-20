from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.pipeline.models.model import Model


class RenderChecks(Model):
    """O que os checks automáticos mediram num MP4 renderizado (CLAUDE.md §4), gravado em
    `renders/checks-<render>.json`. `problems` bloqueia o gate 4; `warnings` fica para a escuta do dono."""

    schema_version: Literal[1] = 1
    render: str  # caminho dentro do episódio, ex.: renders/final.mp4
    sha256: str | None = None  # do MP4 conferido; outro arquivo no lugar invalida a conferência
    checked_at: datetime
    opens: bool
    has_audio: bool
    width: int | None = None
    height: int | None = None
    expected_width: int
    expected_height: int
    duration_ms: int | None = None
    expected_ms: int
    lufs: float | None = None
    long_silences_ms: list[tuple[int, int]] = Field(default_factory=list)
    problems: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems
