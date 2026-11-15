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
    # carimbos de regras anteriores (decisões já gravadas): o arquivo inteiro e o asset_id contado como null
    legacy_hashes: tuple[str, ...] = ()

    @property
    def valid(self) -> bool:
        accepted = {self.current_hash, *self.legacy_hashes} - {None}
        return self.entry is not None and self.entry.input_hash in accepted
