"""Canto da janela do apresentador em cada cena (ADR 013): regra pura sobre os planos, sem renderizar.

A janela fica num canto que o template não usa na cena e muda de canto a cada cena, em sentido horário. O que
o template ocupa vem de `video/src/Scene.tsx` e `Editorial.tsx`: a fonte do plano fica em cima à direita (tela
cheia) ou embaixo à direita (sobre foto ou B-roll), a tarja e o painel do número ficam embaixo à esquerda, e o
título do gráfico em cima à esquerda. Mudou o template, muda a tabela daqui.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.pipeline.schemas import (
    HOST_CORNERS,
    MEDIA_SHOT_KINDS,
    OVERLAY_SHOT_KINDS,
    EpisodeScene,
    HostCorner,
)


def blocked_corners(scene: EpisodeScene) -> set[HostCorner]:
    """Cantos que algum plano da cena ocupa. Cena v1 (só uma foto) não bloqueia canto."""
    blocked: set[HostCorner] = set()
    media_seen = False
    for shot in scene.shots:
        kind = shot.spec.kind
        if kind in MEDIA_SHOT_KINDS:
            layer = "media"
            media_seen = True
        else:  # camadas de Scene.tsx: tarja, carimbo, número e frase vão sobre a mídia anterior
            layer = "overlay" if kind in OVERLAY_SHOT_KINDS and media_seen else "full"
        if shot.source is not None:
            blocked.add("top-right" if layer == "full" else "bottom-right")
        if kind == "lower_third" or (kind == "number" and layer == "overlay"):
            blocked.add("bottom-left")
        if kind == "chart":
            blocked.add("top-left")
        if kind == "compare":  # os rótulos de baixo vão de ponta a ponta
            blocked |= {"bottom-left", "bottom-right"}
    return blocked


def host_corners(scenes: Sequence[EpisodeScene]) -> list[HostCorner]:
    """Um canto por cena. O `host_corner` da cena vale como está; sem ele, o primeiro canto livre depois do
    anterior, em sentido horário. Sem outro canto livre, fica onde estava; se o atual também está ocupado,
    segue o próximo da fila."""
    corners: list[HostCorner] = []
    previous: HostCorner | None = None
    for scene in scenes:
        if scene.host_corner is not None:
            chosen = scene.host_corner
        else:
            start = HOST_CORNERS.index(previous) + 1 if previous else 0
            ring = [HOST_CORNERS[(start + i) % len(HOST_CORNERS)] for i in range(len(HOST_CORNERS))]
            candidates = [c for c in ring if c != previous]
            blocked = blocked_corners(scene)
            stay = [previous] if previous and previous not in blocked else []
            chosen = next((c for c in [*candidates, *stay] if c not in blocked), candidates[0])
        corners.append(chosen)
        previous = chosen
    return corners
