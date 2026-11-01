from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models._schemas_types import RelPath
from app.pipeline.models._schemas_value_shot import Shot
from app.pipeline.models._schemas_value_step_anchors import step_anchors
from app.pipeline.models.model import Model


class EpisodeShot(Model):
    """Plano com tempo resolvido, relativo ao início da cena (ADR 008)."""

    start_ms: int = Field(ge=0)
    duration_ms: int = Field(gt=0)
    spec: Shot
    media: RelPath | None = None  # arquivo do ativo, para foto e B-roll
    source: str | None = None  # "Fonte: …" do rodapé, derivado das claims e do sources.json (ADR 011)
    source_flag: str | None = None  # ressalva ao lado da fonte ("fonte interessada")
    # Entrada de cada parte do plano (`step_anchors`), relativa ao início dele: passos da rede, termos e
    # resultado da conta, linhas e total da nota. Vazio nos outros planos.
    steps_ms: list[int] = []

    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms

    @model_validator(mode="after")
    def _media_when_needed(self) -> Self:
        if (self.spec.kind in SchemasConstants.MEDIA_SHOT_KINDS) != (self.media is not None):
            raise ValueError(f"plano {self.spec.kind}: media é obrigatório para foto/B-roll e só para eles")
        expected = len(step_anchors(self.spec))
        if len(self.steps_ms) != expected:
            raise ValueError(
                f"plano {self.spec.kind}: {len(self.steps_ms)} tempos de passo, esperado {expected}"
            )
        outside = any(not 0 <= ms < self.duration_ms for ms in self.steps_ms)
        if self.steps_ms != sorted(self.steps_ms) or outside:
            raise ValueError(f"tempos dos passos do plano {self.spec.kind} fora de ordem ou fora do plano")
        return self
