from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ScheduledPost:
    """Um agendamento do registro: o `pacote` e o `agendado` com o mesmo payload."""

    episode_id: str | None
    channel: str
    integration_id: str
    scheduled_at: datetime
    post_id: str | None
    media: str | None
