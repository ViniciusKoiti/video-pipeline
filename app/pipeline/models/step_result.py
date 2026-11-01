from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StepResult:
    outputs: list[str]
    needs_review: bool  # True = etapa com gate humano (fica em needs_review até aprovação)
