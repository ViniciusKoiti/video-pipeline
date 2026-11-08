"""O que falta no episódio, fora dos gates, para o `vp status`: peças do vídeo e o que a voz deixou."""

from __future__ import annotations

from app.pipeline.gates import missing_pieces
from app.pipeline.ports import ManifestStore
from app.pipeline.render_checks import render_pending
from app.pipeline.voice_state import voice_pending


def pending_pieces(store: ManifestStore, episode_id: str) -> list[str]:
    return [
        *missing_pieces(store, episode_id),
        *voice_pending(store, episode_id),
        *render_pending(store, episode_id),
    ]
