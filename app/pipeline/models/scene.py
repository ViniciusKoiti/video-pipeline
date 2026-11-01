from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.media.narration import narration_problems, strip_pauses
from app.pipeline.models._schemas_types import AssetId, Delivery, HostCorner, NonEmpty, SceneId, _fold
from app.pipeline.models._schemas_value_shot import Shot
from app.pipeline.models._schemas_value_step_positions import step_positions
from app.pipeline.models.claim import Claim
from app.pipeline.models.hook_shot import HookShot
from app.pipeline.models.keyword_shot import KeywordShot
from app.pipeline.models.model import Model
from app.pipeline.models.status import Status
from app.pipeline.models.visual_need import VisualNeed


class Scene(Model):
    """Uma cena = um bloco de narração = um WAV (ADR 007), com uma lista de planos (ADR 008).
    Sem planos, vale a forma v1: um único plano de foto com os campos visuais da própria cena.
    `delivery` diz como a voz entrega a cena (ADR 022): sem o campo, neutra; `hook`, `turn`, `invite` e `calm`
    variam a ênfase ao longo do vídeo. Só a voz clonada obedece hoje; o Kokoro ignora."""

    id: SceneId
    narration: NonEmpty
    delivery: Delivery | None = None  # ADR 022
    claims: list[Claim] = []
    visual_need: VisualNeed | None = None  # forma v1
    search_query: NonEmpty | None = None  # forma v1
    chosen_asset_id: AssetId | None = None  # forma v1
    shots: list[Shot] = []  # forma v2
    duration_ms: int | None = Field(default=None, gt=0)  # medido da voz real, nunca estimado (§9)
    host_corner: HostCorner | None = None  # ajuste do canto do apresentador nesta cena (ADR 013)
    review_status: Status = Status.PENDING  # reflexo de review.json, escrito pelo código (§5)

    @model_validator(mode="after")
    def _narration_marks(self) -> Self:
        problems = narration_problems(self.narration)
        if problems:
            raise ValueError(f"{self.id}: " + "; ".join(problems))
        return self

    @model_validator(mode="after")
    def _visual_plan(self) -> Self:
        if not self.shots:
            if self.visual_need is None or self.search_query is None:
                raise ValueError(f"{self.id}: cena sem planos precisa de visual_need e search_query")
            return self
        spoken = strip_pauses(self.narration)  # âncoras e frases da tela: texto sem as marcas de pausa
        cursor, positions = 0, []
        for shot in self.shots:
            position = spoken.find(shot.anchor, cursor)
            if position < 0:
                raise ValueError(
                    f"{self.id}: âncora {shot.anchor!r} não aparece na narração depois do plano anterior"
                )
            positions.append(position)
            cursor = position + 1
        ends = [*positions[1:], len(spoken)]
        for shot, start, end in zip(self.shots, positions, ends, strict=True):
            if isinstance(shot, KeywordShot | HookShot) and _fold(shot.text) not in _fold(spoken):
                what = "gancho" if isinstance(shot, HookShot) else "frase na tela"
                raise ValueError(f"{self.id}: {what} {shot.text!r} não está na narração")
            step_positions(spoken, shot, start, end, scene_id=self.id)
        return self
