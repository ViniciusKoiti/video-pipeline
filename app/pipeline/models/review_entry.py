from __future__ import annotations

from typing import Self

from pydantic import AwareDatetime, model_validator

from app.pipeline.models._schemas_types import AssetId, NonEmpty, SceneId
from app.pipeline.models.decision import Decision
from app.pipeline.models.model import Model
from app.pipeline.models.step import Step


class ReviewEntry(Model):
    step: Step
    scene_id: SceneId | None = None  # alvo opcional: uma cena...
    asset_id: AssetId | None = None  # ...ou um ativo; nenhum = a etapa inteira
    decision: Decision
    reviewer: NonEmpty
    at: AwareDatetime
    input_hash: str | None = None  # hash do conteúdo revisado; mudou → a aprovação não vale (§5)
    choice: str | None = None  # valor escolhido pelo humano quando difere da recomendação (ex.: formato)
    notes: str = ""

    @model_validator(mode="after")
    def _single_target(self) -> Self:
        if self.scene_id is not None and self.asset_id is not None:
            raise ValueError("uma entrada revisa a etapa, uma cena ou um ativo, não ambos")
        return self
