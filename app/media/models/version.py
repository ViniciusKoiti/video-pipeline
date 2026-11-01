from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.media.models.sample import Sample


class Version(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    episode_id: str
    rendered_at: str  # hora do arquivo renderizado
    commit: str
    template_hash: str
    motion_kit: str
    sha256: str
    duration_ms: int
    render_s: float | None = None
    cpu_probe_s: float | None = None
    note: str
    samples: list[Sample]
    changed: list[str] | None = None  # planos que mudaram em relação à versão anterior; None na primeira
