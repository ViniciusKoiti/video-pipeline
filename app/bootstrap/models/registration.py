from __future__ import annotations

from dataclasses import dataclass
from typing import Generic

from app.bootstrap.models._bootstrap_registry_types import Factory, T_co


@dataclass(frozen=True)
class Registration(Generic[T_co]):
    step: int
    factory: Factory[T_co] | None = None
