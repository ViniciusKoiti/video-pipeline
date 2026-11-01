from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import AssetId, Delivery, HostCorner, NonEmpty, RelPath, SceneId
from app.pipeline.models.episode_shot import EpisodeShot
from app.pipeline.models.model import Model


class EpisodeScene(Model):
    id: SceneId
    start_ms: int = Field(ge=0)
    duration_ms: int = Field(gt=0)
    narration: NonEmpty
    audio: RelPath
    asset_id: AssetId | None = None  # v1: um visual por cena
    image: RelPath | None = None  # v1
    shots: list[EpisodeShot] = []  # v2: planos cobrindo a cena inteira
    host_corner: HostCorner | None = None  # ajuste do canto do apresentador (ADR 013)
    # Entrega da fala (ADR 022), copiada do roteiro: dá a expressão do apresentador (ADR 029).
    delivery: Delivery | None = None

    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms

    @model_validator(mode="after")
    def _one_visual_form(self) -> Self:
        if self.shots:
            if self.image is not None or self.asset_id is not None:
                raise ValueError(f"{self.id}: use image/asset_id (v1) ou shots (v2), não os dois")
            cursor = 0
            for shot in self.shots:
                if shot.start_ms != cursor:
                    raise ValueError(f"{self.id}: planos com buraco ou sobreposição em {shot.start_ms} ms")
                cursor = shot.end_ms
            if cursor != self.duration_ms:
                raise ValueError(f"{self.id}: planos somam {cursor} ms, a cena tem {self.duration_ms} ms")
        elif self.image is None or self.asset_id is None:
            raise ValueError(f"{self.id}: cena sem planos precisa de image e asset_id (v1)")
        return self
