"""Porta de geração de texto. O adapter só transporta: prompt e schema entram, objeto validado sai.
Prompts, recuperação de trechos e validação de claims ficam no pipeline (ADR 006)."""

from __future__ import annotations

from typing import Protocol

from app.providers.base import ProviderInfo
from app.providers.text.models._base_types import T as T
from app.providers.text.models.text_request import TextRequest as TextRequest
from app.providers.text.models.text_result import TextResult as TextResult
from app.providers.text.models.usage import Usage as Usage


class TextProvider(Protocol):
    info: ProviderInfo

    def generate_json(self, request: TextRequest[T]) -> TextResult[T]: ...
