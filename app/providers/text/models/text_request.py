from __future__ import annotations

from dataclasses import dataclass
from typing import Generic

from app.providers.text.models._base_types import T


@dataclass(frozen=True)
class TextRequest(Generic[T]):
    prompt: str
    output: type[T]  # o adapter pede JSON neste schema e valida a resposta; falha → InvalidOutput
    system: str = ""
    temperature: float = 0.0
    max_tokens: int | None = None
    model: str | None = None  # None = modelo configurado; outro valor só por escolha explícita (vp bench)
