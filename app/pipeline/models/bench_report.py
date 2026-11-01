from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.pipeline.models.llm_run import LlmRun
from app.pipeline.models.machine import Machine
from app.pipeline.models.render_run import RenderRun
from app.pipeline.models.tts_run import TtsRun


class BenchReport(BaseModel):
    created_at: datetime
    machine: Machine
    warnings: list[str]
    llm: list[LlmRun]
    tts: list[TtsRun]
    render: list[RenderRun] = []
    peak_rss_mb: int  # deste processo (inclui o Kokoro); o Ollama roda em outro processo
