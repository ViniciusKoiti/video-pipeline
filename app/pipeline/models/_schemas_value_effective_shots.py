from __future__ import annotations

from typing import TYPE_CHECKING

from app.media.narration import strip_pauses
from app.pipeline.models.photo_shot import PhotoShot

if TYPE_CHECKING:
    from app.pipeline.models._schemas_value_shot import Shot
    from app.pipeline.models.scene import Scene


def effective_shots(scene: Scene) -> list[Shot]:
    """Planos da cena; a forma v1 vira um único plano de foto sobre a narração inteira."""
    if scene.shots:
        return list(scene.shots)
    return [
        PhotoShot(
            anchor=strip_pauses(scene.narration),
            visual_need=scene.visual_need,  # type: ignore[arg-type]  # garantido pelo validador da cena
            search_query=scene.search_query,  # type: ignore[arg-type]
            asset_id=scene.chosen_asset_id,
        )
    ]
