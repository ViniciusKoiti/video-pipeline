from __future__ import annotations

from app.pipeline.models._sfx_types import COVERS_SPEECH
from app.pipeline.models.model import Model


class SfxSound(Model):
    """O que usamos do registro de um som no `sounds.json` do kit."""

    id: str
    file: str
    duration: float
    sync_at: float
    meets: str
    onset: float
    body_end: float
    under_voiceover_db: float
    avoid_for: list[str] = []
    fits_seconds: tuple[float, float] | None = None
    sha256: str

    @property
    def covers_speech(self) -> bool:
        return any(a.startswith(COVERS_SPEECH) for a in self.avoid_for)
