from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

from app.pipeline.models.brief_action import BriefAction


@dataclass(frozen=True)
class BriefInstall:
    action: BriefAction
    brief: BaseModel  # o resumo já validado pelo contrato dele
    archived: str | None = None  # nome do arquivo do anterior, quando houve troca
