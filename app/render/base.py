"""Porta do motor de montagem: `episode.json` é a única entrada (§6)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.pipeline.schemas import EpisodeManifest, VideoSpec
from app.providers.base import ProviderInfo

PREVIEW_HEIGHT = 720


@dataclass(frozen=True)
class RenderResult:
    path: Path
    width: int
    height: int
    duration_ms: int


def target_spec(episode: EpisodeManifest, *, preview: bool) -> VideoSpec:
    """Formato de saída: o do episódio, ou 1280×720 na prévia."""
    if not preview:
        return episode.video
    return episode.video.model_copy(update={"width": PREVIEW_HEIGHT * 16 // 9, "height": PREVIEW_HEIGHT})


class RenderEngine(Protocol):
    info: ProviderInfo

    def render(
        self, episode: EpisodeManifest, episode_dir: Path, out: Path, *, preview: bool = False
    ) -> RenderResult: ...
