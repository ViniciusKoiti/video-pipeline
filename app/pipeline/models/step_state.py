from __future__ import annotations

from pydantic import AwareDatetime

from app.pipeline.models._schemas_types import RelPath
from app.pipeline.models.model import Model
from app.pipeline.models.status import Status


class StepState(Model):
    status: Status = Status.PENDING
    input_hash: str | None = None
    outputs: list[RelPath] = []  # arquivos gerados, relativos à pasta do episódio
    started_at: AwareDatetime | None = None
    finished_at: AwareDatetime | None = None
    error: str = ""  # motivo da última falha (ex.: "quota_exhausted: ...")
