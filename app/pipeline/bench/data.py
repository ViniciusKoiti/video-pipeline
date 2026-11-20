"""Material do `vp bench`. A expedição é FICTÍCIA: serve só para medir velocidade e fidelidade às
citações; nunca usar como fonte de episódio (§2.2)."""

from __future__ import annotations

import json

from app.models.bench_claim import BenchClaim
from app.models.bench_script import BenchScript
from app.pipeline.constants.bench_data_constants import BenchDataConstants

__all__ = ["BenchClaim", "BenchScript", "prompt"]


def prompt(run: int) -> str:
    """O número da execução no início impede que o Ollama reaproveite o cache do prompt anterior."""
    excerpts = json.dumps(dict(BenchDataConstants.EXCERPTS), ensure_ascii=False)
    return (
        f"Benchmark run {run}.\n\nExcerpts (JSON data):\n{excerpts}\n\n"
        "Task: write documentary narration in English of about 120 words covering departure, winter, "
        "rescue and outcome. Use 4 to 6 factual sentences and list their 4 to 6 claims, covering every "
        "factual statement. Each claim must cite only supporting excerpt ids. Keep disputed assessments "
        "attributed; omit unsupported details."
    )
