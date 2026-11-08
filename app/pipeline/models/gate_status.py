from __future__ import annotations

from dataclasses import dataclass

from app.pipeline.models.review_entry import ReviewEntry
from app.pipeline.models.step import Step


@dataclass(frozen=True)
class GateStatus:
    step: Step
    asset_id: str | None
    entry: ReviewEntry | None  # última decisão; None = nenhuma
    current_hash: str | None  # None = o que foi revisto não existe mais
    legacy_hash: str | None = None  # carimbo de antes de a imagem sair do gate 2 (decisões já gravadas)

    @property
    def valid(self) -> bool:
        accepted = {self.current_hash, self.legacy_hash} - {None}
        return self.entry is not None and self.entry.input_hash in accepted
