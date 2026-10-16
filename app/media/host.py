"""Canto da janela do apresentador em cada cena (ADR 013): regra pura sobre os planos, sem renderizar.

A janela fica num canto que o template não usa na cena e muda de canto a cada cena, em sentido horário. O que
o template ocupa vem de `video/src/Scene.tsx` e `Editorial.tsx`: a fonte do plano fica em cima à direita (tela
cheia) ou embaixo à direita (sobre foto ou B-roll), a tarja e o painel do número ficam embaixo à esquerda, e o
título do gráfico em cima à esquerda. Mudou o template, muda a tabela daqui.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

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


# Pele em camadas (ADR 029): com `sprites.json` na pasta, valem as camadas que ele cita, no formato
# `host-sprites.v1` do motion-kit; sem ele, as 12 imagens inteiras da ADR 017.
MANIFEST_FILE = "sprites.json"
KIT_CLI = Path("node_modules/@viniciusk/motion-kit/bin/motion-kit.mjs")  # dentro de `video/`


class SpriteCheckError(RuntimeError):
    """A pasta da pele não passou na conferência do motion-kit."""


def sprites_manifest(episode_dir: Path) -> dict[str, Any] | None:
    """O `sprites.json` da pele `dono`, ou `None` na pele de 12 imagens."""
    file = episode_dir / SPRITES_DIR / MANIFEST_FILE
    return json.loads(file.read_text()) if file.is_file() else None


def check_sprites(episode_dir: Path, project: Path, *, node: str = "node") -> None:
    """Confere a pasta pelo comando do kit instalado em `video/` (`motion-kit sprites check`): o formato é
    do kit, e o Python não o reimplementa. Para com a mensagem do comando."""
    folder = episode_dir / SPRITES_DIR
    result = subprocess.run(
        [node, str(project / KIT_CLI), "sprites", "check", str(folder)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SpriteCheckError(f"pele dono: {(result.stderr or result.stdout).strip()}")


def sprite_files(episode_dir: Path) -> list[Path]:
    """As imagens da pele `dono`. Com `sprites.json`, o manifesto e os arquivos que ele cita; sem ele, cada
    visema de olho aberto e de olho fechado (`<visema>-piscada.png`)."""
    folder = episode_dir / SPRITES_DIR
    manifest = sprites_manifest(episode_dir)
    if manifest is not None:
        cited = sorted({str(sprite["file"]) for sprite in manifest.get("sprites", [])})
        return [folder / MANIFEST_FILE, *(folder / name for name in cited)]
    return [folder / f"{viseme}{blink}.png" for viseme in VISEMES for blink in ("", "-piscada")]


def sprites_hash(episode_dir: Path) -> str:
    """Hash das imagens (e do manifesto) e do registro de origem; entra nas props da cena, e com isso no cache
    do render. Falta de imagem ou de registro é erro: ativo sem origem registrada não entra no render
    (§2.3)."""
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


# --- direção automática (ADR 029) --------------------------------------------------------------------

# Planos em que o apresentador aponta para o conteúdo quando entram.
POINT_SHOT_KINDS = frozenset({"number", "compare", "calculation", "receipt", "chart"})
POINT_MS = 1500
# Expressão pela entrega da fala (ADR 022); as outras entregas ficam na neutra.
DELIVERY_EXPRESSIONS = {"hook": "raised", "turn": "furrow"}
# O ciclo de gesticular do `<Host>` (repouso ↔ explicando, 21 quadros por gesto), escrito por extenso nas
# cenas em que ele aponta: o kit não mistura gesto agendado com o ciclo.
GESTURE_CYCLE = ("rest", "open")
GESTURE_EVERY = 21


def host_direction(scene: EpisodeScene, corner: HostCorner, fps: int) -> dict[str, Any]:
    """A direção do apresentador na cena, sem campo no roteiro: olha para o lado do conteúdo (janela à
    direita olha para a esquerda), aponta por ~1,5 s quando entra um número, uma comparação, uma conta, uma
    nota ou um gráfico, gesticula no resto da fala, e a expressão segue a entrega (`hook` ergue a
    sobrancelha, `turn` franze). O que a pele não desenha cai no repouso. Quadros relativos à cena."""
    frames = max(1, round(scene.duration_ms * fps / 1000))
    direction: dict[str, Any] = {
        "look": "left" if corner.endswith("right") else "right",
        "expression": DELIVERY_EXPRESSIONS.get(scene.delivery or "neutral", "neutral"),
    }
    windows: list[tuple[int, int]] = []
    for shot in scene.shots:
        if shot.spec.kind not in POINT_SHOT_KINDS:
            continue
        start = round(shot.start_ms * fps / 1000)
        end = min(frames, start + round(POINT_MS * fps / 1000))
        if windows and start <= windows[-1][1]:  # apontar de novo emenda com o anterior
            windows[-1] = (windows[-1][0], max(windows[-1][1], end))
        else:
            windows.append((start, end))
    if not windows:
        direction["gesticulate"] = True
        return direction
    cues: list[dict[str, Any]] = []
    cursor = 0
    for start, end in windows:
        # o ciclo para meia volta antes de apontar: um gesto de poucos quadros antes do apontar só pisca
        cues += [
            {"at": at, "gesture": GESTURE_CYCLE[i % len(GESTURE_CYCLE)]}
            for i, at in enumerate(range(cursor, start - GESTURE_EVERY // 2, GESTURE_EVERY))
        ]
        cues.append({"at": start, "gesture": "point"})
        cursor = end
    cues += [
        {"at": at, "gesture": GESTURE_CYCLE[i % len(GESTURE_CYCLE)]}
        for i, at in enumerate(range(cursor, frames, GESTURE_EVERY))
    ]
    direction["gestures"] = cues
    return direction
