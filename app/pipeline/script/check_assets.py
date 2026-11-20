"""Os ativos que o `vp check` confere: todos os `assets/*.json` legíveis, ou só os dos planos de mídia."""

from __future__ import annotations

from app.pipeline.models.check_report import CheckReport
from app.pipeline.ports import ManifestInvalid, ManifestStore
from app.pipeline.schemas import Asset, BrollShot, PhotoShot, Shot
from app.pipeline.script.reading import read_optional


def episode_assets(store: ManifestStore, episode_id: str) -> dict[str, Asset]:
    """Todos os `assets/*.json` legíveis; o que não passa no schema fica de fora sem virar erro aqui."""
    folder = store.path(episode_id, "assets")
    found = {}
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        try:
            found[path.stem] = store.read(episode_id, f"assets/{path.name}", Asset)
        except ManifestInvalid:
            continue
    return found


def planned_assets(
    store: ManifestStore, episode_id: str, planned: list[tuple[str, Shot, float]], report: CheckReport
) -> dict[str, Asset]:
    """Ativos já registrados (`assets/<id>.json`) dos planos de foto e B-roll; o não escolhido fica fora."""
    media = (shot for _, shot, _ in planned if isinstance(shot, PhotoShot | BrollShot))
    ids = {shot.asset_id for shot in media if shot.asset_id}
    found = {}
    for asset_id in sorted(ids):
        if (asset := read_optional(store, episode_id, f"assets/{asset_id}.json", Asset, report)) is not None:
            found[asset_id] = asset
    return found
