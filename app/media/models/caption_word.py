from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CaptionWord:
    text: str
    start_ms: int
    end_ms: int
    matched: bool  # False = tempo dividido entre as vizinhas que casaram
