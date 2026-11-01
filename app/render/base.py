"""Porta do motor de montagem: `episode.json` é a única entrada (§6)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.pipeline.schemas import EpisodeManifest, VideoSpec
from app.providers.base import ProviderInfo
from app.render.models.render_result import RenderResult as RenderResult

PREVIEW_HEIGHT = 720


def target_spec(episode: EpisodeManifest, *, preview: bool) -> VideoSpec:
    """Formato de saída: o do episódio, ou 1280×720 na prévia."""
    if not preview:
        return episode.video
    long_side = PREVIEW_HEIGHT * 16 // 9  # o lado curto vale PREVIEW_HEIGHT nos dois perfis
    size = {"width": PREVIEW_HEIGHT, "height": long_side} if episode.video.portrait else {
        "width": long_side, "height": PREVIEW_HEIGHT}
    return episode.video.model_copy(update=size)


class RenderEngine(Protocol):
    info: ProviderInfo

    def render(
        self, episode: EpisodeManifest, episode_dir: Path, out: Path, *, preview: bool = False
    ) -> RenderResult: ...
