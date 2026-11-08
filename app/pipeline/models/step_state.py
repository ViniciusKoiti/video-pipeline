from __future__ import annotations

from pydantic import AwareDatetime

from app.pipeline.models._schemas_types import RelPath
from app.pipeline.models.model import Model
from app.pipeline.models.scene_record import SceneRecord
from app.pipeline.models.status import Status


class StepState(Model):
    status: Status = Status.PENDING
    input_hash: str | None = None
    outputs: list[RelPath] = []  # arquivos gerados, relativos à pasta do episódio
    started_at: AwareDatetime | None = None
    finished_at: AwareDatetime | None = None
    error: str = ""  # motivo da última falha (ex.: "quota_exhausted: ...")
    scenes: dict[str, SceneRecord] = {}  # etapas por cena (voz, imagens): um registro por cena tentada

    @property
    def pending_scenes(self) -> list[str]:
        """Cenas tentadas que ainda não terminaram (falha recuperável ou bloqueio): produção incompleta."""
        return [scene_id for scene_id, record in self.scenes.items() if record.status is not Status.COMPLETED]
