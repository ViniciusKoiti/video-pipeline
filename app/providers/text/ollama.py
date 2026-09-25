"""Adapter Ollama local com structured outputs (§7). Parâmetros explícitos; nada de settings aqui."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput, ModelUnavailable, ProviderError
from app.providers.http import JsonPost, TransportError, post_json
from app.providers.text.base import TextRequest, TextResult, Usage

T = TypeVar("T", bound=BaseModel)
NS_PER_MS = 1_000_000


class OllamaText:
    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        num_thread: int = 8,
        timeout_s: float = 1800,  # CPU lenta: um roteiro pode levar dezenas de minutos (ADR 004)
        keep_alive: str = "5m",
        post: JsonPost = post_json,
    ) -> None:
        self.info = ProviderInfo("ollama", remote=False)
        self._url = base_url.rstrip("/") + "/api/chat"
        self._model = model
        self._num_thread = num_thread
        self._timeout_s = timeout_s
        self._keep_alive = keep_alive
        self._post = post

    def generate_json(self, request: TextRequest[T]) -> TextResult[T]:
        model = request.model or self._model
        messages = [{"role": "system", "content": request.system}] if request.system else []
        messages.append({"role": "user", "content": request.prompt})
        options: dict[str, Any] = {"temperature": request.temperature, "num_thread": self._num_thread}
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        payload = {
            "model": model,
            "messages": messages,
            "format": request.output.model_json_schema(),
            "stream": False,
            "think": False,
            "keep_alive": self._keep_alive,
            "options": options,
        }
        try:
            response = self._post(self._url, payload, self._timeout_s)
        except TransportError as error:
            if error.status == 404:
                message = f"modelo {model!r} ausente (ollama pull {model})"
                raise ModelUnavailable(self.info.name, message) from None
            raise ProviderError(self.info.name, str(error)) from None
        if response.get("done_reason") == "length":
            raise InvalidOutput(self.info.name, f"resposta cortada no limite de {request.max_tokens} tokens")
        try:
            data = request.output.model_validate_json(response.get("message", {}).get("content", ""))
        except ValidationError as error:
            message = f"resposta fora do schema {request.output.__name__} ({error.error_count()} erros)"
            raise InvalidOutput(self.info.name, message) from None
        return TextResult(data=data, model=str(response.get("model", model)), usage=_usage(response))


def _ms(response: dict[str, Any], key: str) -> int | None:
    value = response.get(key)
    return None if value is None else int(value) // NS_PER_MS


def _usage(response: dict[str, Any]) -> Usage:
    return Usage(
        input_tokens=int(response.get("prompt_eval_count", 0)),
        output_tokens=int(response.get("eval_count", 0)),
        duration_ms=_ms(response, "total_duration") or 0,
        load_ms=_ms(response, "load_duration"),
        prompt_ms=_ms(response, "prompt_eval_duration"),
        generation_ms=_ms(response, "eval_duration"),
        cached_input_tokens=response.get("prompt_eval_cached_count"),
    )
