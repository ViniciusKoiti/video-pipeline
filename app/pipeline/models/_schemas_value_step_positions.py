from __future__ import annotations

from typing import TYPE_CHECKING

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models._schemas_value_step_anchors import step_anchors

if TYPE_CHECKING:
    from app.pipeline.models._schemas_value_shot import Shot


def step_positions(narration: str, shot: Shot, start: int, end: int, *, scene_id: str) -> list[int]:
    """Posição, na narração, da âncora de cada parte do plano (`step_anchors`): em ordem, dentro do trecho do
    plano ([`start`, `end`), até a âncora do plano seguinte). Parte sem âncora entra com o plano."""
    cursor, positions = start, []
    for anchor in step_anchors(shot):
        if anchor is None:
            positions.append(start)
            continue
        position = narration.find(anchor, cursor)
        if position < 0 or position >= end:
            where = "da rede" if shot.kind == "network" else f"do plano {shot.kind}"
            raise ValueError(

        f'{scene_id}: {SchemasConstants._STEP_NAMES[shot.kind]} {anchor!r} {where}'
        f' não aparece na narração, em ordem, dentro do trecho do plano'

            )
        positions.append(position)
        cursor = position + 1
    return positions
