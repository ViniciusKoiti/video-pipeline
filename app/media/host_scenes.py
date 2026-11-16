"""O apresentador cena a cena (ADR 013, 056): em que cenas aparece, com que canto e que props recebe.

Com `host.show = "all"` e sem marca nas cenas, é o que o motor sempre fez: um canto por cena, as mesmas props.
Nas cenas sem apresentador não há props `host` (a janela não ocupa canto nem reserva espaço) e o canto avança
em sentido horário só entre as cenas com ele. A primeira cena com apresentador depois de uma sem ele não tem
`fromCorner`: a janela entra, em vez de vir arrastada do canto anterior."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.media.envelope import mouth_levels
from app.media.host import host_corners, host_direction, sprites_hash, sprites_manifest
from app.pipeline.schemas import EpisodeManifest, HostCorner, HostSpec


def host_identity(host: HostSpec) -> dict[str, Any]:
    """Identidade do `<Host>` do motion-kit (camelCase, como a pele Notionists a lê); só as peças dadas.
    A pele `dono` não tem peças: só o nome dela."""
    identity = host.identity
    if identity is None:
        return {"skin": host.skin}
    parts = {
        "hair": identity.hair,
        "outfit": identity.outfit,
        "eyes": identity.eyes,
        "brows": identity.brows,
        "facialHair": identity.facial_hair,
        "glasses": identity.glasses,
    }
    result: dict[str, Any] = {"skin": host.skin, **{k: v for k, v in parts.items() if v is not None}}
    if identity.nose is not None:
        result["extras"] = {"nose": identity.nose}
    return result


def scene_corners(episode: EpisodeManifest) -> list[HostCorner | None]:
    """O canto de cada cena, ou `None` onde o apresentador não aparece. A regra de cantos corre só sobre as
    cenas com ele."""
    if episode.host is None:
        return [None] * len(episode.scenes)
    shown = [s for s in episode.scenes if episode.host.shows(s.host)]
    chosen = iter(host_corners(shown, portrait=episode.video.portrait))
    return [next(chosen) if episode.host.shows(s.host) else None for s in episode.scenes]


def host_props(
    episode: EpisodeManifest,
    episode_dir: Path,
    corners: list[HostCorner | None],
    index: int,
    fps: int,
    frames: int,
) -> dict[str, Any] | None:
    """As props `host` da cena `index`, ou `None` sem apresentador nela (props e cache ficam como estavam)."""
    host, corner, scene = episode.host, corners[index], episode.scenes[index]
    if host is None or corner is None:
        return None
    props: dict[str, Any] = {
        "identity": host_identity(host),
        "width": host.width_for(portrait=episode.video.portrait),
        "corner": corner,
        "fromCorner": corners[index - 1] if index > 0 else None,
        "levels": mouth_levels(episode_dir / scene.audio, fps, frames),
        "direction": host_direction(scene, corner, fps),  # ADR 029
    }
    if host.skin == "dono":  # trocar o desenho refaz as cenas (cache por props)
        props["sprites"] = sprites_hash(episode_dir)
        if (manifest := sprites_manifest(episode_dir)) is not None:  # pele em camadas (ADR 029)
            props["manifest"] = manifest
    return props
