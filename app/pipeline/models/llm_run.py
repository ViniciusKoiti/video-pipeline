from __future__ import annotations

from pydantic import BaseModel

from app.pipeline.models.bench_script import BenchScript


class LlmRun(BaseModel):
    provider: str
    model: str
    run: int
    prompt_sha256: str = ""  # relatórios antigos não registravam o prompt
    ok: bool
    error: str = ""
    wall_s: float
    input_tokens: int = 0
    cached_input_tokens: int | None = None
    output_tokens: int = 0
    load_s: float | None = None
    prompt_tok_s: float | None = None
    generation_tok_s: float | None = None
    claims: int = 0
    unknown_excerpts: list[str] = []
    mem_available_mb_after: int = 0
    output: BenchScript | None = None  # texto gerado, para avaliação humana de fidelidade (§7)
