from __future__ import annotations

from dataclasses import dataclass
from typing import Generic

from app.providers.text.models._base_types import T
from app.providers.text.models.usage import Usage


@dataclass(frozen=True)
class TextResult(Generic[T]):
    data: T
    model: str
    usage: Usage
