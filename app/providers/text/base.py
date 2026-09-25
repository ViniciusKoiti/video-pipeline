"""Porta de geração de texto. O adapter só transporta: prompt e schema entram, objeto validado sai.
Prompts, recuperação de trechos e validação de claims ficam no pipeline (ADR 006)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel

from app.providers.base import ProviderInfo

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class TextRequest(Generic[T]):
    prompt: str
    output: type[T]  # o adapter pede JSON neste schema e valida a resposta; falha → InvalidOutput
    system: str = ""
    temperature: float = 0.0
    max_tokens: int | None = None
    model: str | None = None  # None = modelo configurado; outro valor só por escolha explícita (vp bench)


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


@dataclass(frozen=True)
class TextResult(Generic[T]):
    data: T
    model: str
    usage: Usage


class TextProvider(Protocol):
    info: ProviderInfo

    def generate_json(self, request: TextRequest[T]) -> TextResult[T]: ...
