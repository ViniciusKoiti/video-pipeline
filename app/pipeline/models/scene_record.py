from __future__ import annotations

from app.pipeline.models._schemas_types import RelPath
from app.pipeline.models.model import Model
from app.pipeline.models.status import Status


class SceneRecord(Model):
    """O que uma cena de uma etapa deixou no `manifest.json`, para retomar sem estado em memória.

    `COMPLETED`: a ação terminou e os `outputs` existiam ao ser gravada. `NEEDS_REVIEW`: falha recuperável
    de provedor (`reason`, `detail`). `PENDING`: não tentada ou bloqueada por outra cena (`reason="blocked"`).
    """

    status: Status = Status.PENDING
    outputs: list[RelPath] = []
    reason: str = ""
    detail: str = ""
