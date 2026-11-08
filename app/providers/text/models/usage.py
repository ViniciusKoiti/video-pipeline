from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int
    duration_ms: int
    # Detalhamento opcional, quando o provedor informa (usado pelo vp bench):
    load_ms: int | None = None
    prompt_ms: int | None = None
    generation_ms: int | None = None
    cached_input_tokens: int | None = None
