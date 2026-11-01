from __future__ import annotations

from app.pipeline.models._schemas_types import EpisodeId
from app.pipeline.models.decision import Decision
from app.pipeline.models.model import Model
from app.pipeline.models.review_entry import ReviewEntry
from app.pipeline.models.step import Step


class ReviewLog(Model):
    """Fonte única das decisões humanas (§5, ADR 007). Só cresce: entradas nunca são editadas."""

    episode_id: EpisodeId
    entries: list[ReviewEntry] = []

    def latest(
        self, step: Step, *, scene_id: str | None = None, asset_id: str | None = None
    ) -> ReviewEntry | None:
        matches = [e for e in self.entries if (e.step, e.scene_id, e.asset_id) == (step, scene_id, asset_id)]
        return max(matches, key=lambda e: e.at) if matches else None

    def is_approved(
        self,
        step: Step,
        *,
        scene_id: str | None = None,
        asset_id: str | None = None,
        input_hash: str | None = None,
    ) -> bool:
        entry = self.latest(step, scene_id=scene_id, asset_id=asset_id)
        if entry is None or entry.decision is not Decision.APPROVED:
            return False
        return input_hash is None or entry.input_hash == input_hash
