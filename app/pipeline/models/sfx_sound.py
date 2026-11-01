from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from app.pipeline.constants.sfx_constants import SfxConstants
from app.pipeline.models._schemas_types import NonEmpty, RelPath, Sha256
from app.pipeline.models.model import Model


class SfxSound(Model):
    """O que usamos do registro de um som no `sounds.json` do kit. As invariantes valem na leitura (RF5):
    durações e tempos finitos, `0 <= sync_at <= duration`, `0 <= onset <= body_end <= duration`, arquivo
    relativo à pasta do kit e `sha256` bem formado."""

    id: NonEmpty
    file: RelPath
    duration: float = Field(gt=0, allow_inf_nan=False)
    sync_at: float = Field(ge=0, allow_inf_nan=False)
    meets: str
    onset: float = Field(ge=0, allow_inf_nan=False)
    body_end: float = Field(ge=0, allow_inf_nan=False)
    under_voiceover_db: float = Field(allow_inf_nan=False)
    avoid_for: list[str] = []
    fits_seconds: tuple[float, float] | None = None
    sha256: Sha256

    @model_validator(mode="after")
    def _times_fit_the_sound(self) -> Self:
        slack = SfxConstants.TIME_SLACK_S
        if self.sync_at > self.duration + slack:
            raise ValueError(f"sync.at ({self.sync_at}) passa da duração ({self.duration})")
        if self.onset > self.body_end:
            raise ValueError(f"timing.onset ({self.onset}) vem depois de timing.body_end ({self.body_end})")
        if self.body_end > self.duration + slack:
            raise ValueError(f"timing.body_end ({self.body_end}) passa da duração ({self.duration})")
        return self

    @property
    def covers_speech(self) -> bool:
        return any(a.startswith(SfxConstants.COVERS_SPEECH) for a in self.avoid_for)
