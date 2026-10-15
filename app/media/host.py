"""Canto da janela do apresentador em cada cena (ADR 013): regra pura sobre os planos, sem renderizar.

A janela fica num canto que o template não usa na cena e muda de canto a cada cena, em sentido horário. O que
o template ocupa vem de `video/src/Scene.tsx` e `Editorial.tsx`: a fonte do plano fica em cima à direita (tela
cheia) ou embaixo à direita (sobre foto ou B-roll), a tarja e o painel do número ficam embaixo à esquerda, e o
título do gráfico em cima à esquerda. Mudou o template, muda a tabela daqui.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from pathlib import Path

from app.pipeline.schemas import (
    HOST_CORNERS,
    MEDIA_SHOT_KINDS,
    OVERLAY_SHOT_KINDS,
    EpisodeScene,
    HostCorner,
)

# --- pele `dono` (ADR 017, parte A) ------------------------------------------------------------------

SPRITES_DIR = "host/dono"  # dentro da pasta do episódio, que é a pasta pública do render e fica fora do Git
VISEMES = ("rest", "mbp", "ei", "a", "ou", "fv")  # o vocabulário do `<Host>` do motion-kit
ORIGIN_FILE = "origem.json"  # de onde veio o desenho: autor, gerador e licença (§2.3)


def sprite_files(episode_dir: Path) -> list[Path]:
    """As 12 imagens da pele `dono`: cada visema de olho aberto e de olho fechado (`<visema>-piscada.png`)."""
    folder = episode_dir / SPRITES_DIR
    return [folder / f"{viseme}{blink}.png" for viseme in VISEMES for blink in ("", "-piscada")]


def sprites_hash(episode_dir: Path) -> str:
    """Hash das imagens e do registro de origem; entra nas props da cena, e com isso no cache do render.
    Falta de imagem ou de registro é erro: ativo sem origem registrada não entra no render (§2.3)."""
    files = [*sprite_files(episode_dir), episode_dir / SPRITES_DIR / ORIGIN_FILE]
    missing = [f.name for f in files if not f.is_file()]
    if missing:
        raise FileNotFoundError(f"pele dono: faltam em {SPRITES_DIR}/: {', '.join(missing)}")
    digest = hashlib.sha256()
    for file in files:
        digest.update(file.name.encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()[:16]


def blocked_corners(scene: EpisodeScene, *, portrait: bool = False) -> set[HostCorner]:
    """Cantos que algum plano da cena ocupa. Cena v1 (só uma foto) não bloqueia canto.

    Em retrato (ADR 014) só os cantos de cima são livres: o conteúdo fica centralizado e a base segura das
    plataformas reserva a faixa de baixo, então os cantos de baixo caem no meio do quadro e ficam bloqueados
    (menos numa cena só de gráficos, que ficam alinhados ao topo). A janela vem logo abaixo da fonte, que fica
    no topo. O selo no canto e o título do gráfico tomam o topo; a comparação empilhada começa abaixo da
    janela (template: COMPARE_TOP) e não toma canto."""
    # Em retrato o conteúdo é centralizado, menos o gráfico (no alto): cena só de gráficos libera os de baixo.
    centered = any(shot.spec.kind != "chart" for shot in scene.shots) or not scene.shots
    blocked: set[HostCorner] = {"bottom-left", "bottom-right"} if portrait and centered else set()
    media_seen = False
    for shot in scene.shots:
        kind = shot.spec.kind
        if kind in MEDIA_SHOT_KINDS:
            layer = "media"
            media_seen = True
        else:  # camadas de Scene.tsx: tarja, carimbo, número e frase vão sobre a mídia anterior
            layer = "overlay" if kind in OVERLAY_SHOT_KINDS and media_seen else "full"
        if portrait:
            if kind == "chart":
                blocked |= {"top-left", "top-right"}
            if kind == "stamp" and layer == "overlay":
                blocked.add("top-left")
            continue
        if shot.source is not None:
            blocked.add("top-right" if layer == "full" else "bottom-right")
        if kind == "lower_third" or (kind == "number" and layer == "overlay"):
            blocked.add("bottom-left")
        if kind == "chart":
            blocked.add("top-left")
        if kind == "compare":  # os rótulos de baixo vão de ponta a ponta
            blocked |= {"bottom-left", "bottom-right"}
    return blocked


def host_corners(scenes: Sequence[EpisodeScene], *, portrait: bool = False) -> list[HostCorner]:
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
            blocked = blocked_corners(scene, portrait=portrait)
            stay = [previous] if previous and previous not in blocked else []
            chosen = next((c for c in [*candidates, *stay] if c not in blocked), candidates[0])
        corners.append(chosen)
        previous = chosen
    return corners
