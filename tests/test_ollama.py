from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from pydantic import BaseModel

from app.providers.errors import InvalidOutput, ModelUnavailable, ProviderError
from app.providers.http import TransportError
from app.providers.text.base import TextRequest
from app.providers.text.ollama import OllamaText
from tests.fakes import fake_ollama_post


class Reply(BaseModel):
    text: str


OK = Reply(text="ok").model_dump_json()
REQUEST = TextRequest(prompt="p", output=Reply)


def test_request_uses_structured_output_and_local_settings() -> None:
    post, calls = fake_ollama_post([OK])
    provider = OllamaText("http://127.0.0.1:11434/", "qwen3.5:9b", num_thread=8, timeout_s=60, post=post)
    provider.generate_json(TextRequest(prompt="Say ok", output=Reply, system="Be brief", max_tokens=50))
    call = calls[0]
    assert call["url"] == "http://127.0.0.1:11434/api/chat"
    assert call["timeout"] == 60
    payload = call["payload"]
    assert payload["model"] == "qwen3.5:9b"
    assert payload["format"] == Reply.model_json_schema()
    assert (payload["stream"], payload["think"]) == (False, False)
    assert payload["options"] == {"temperature": 0.0, "num_thread": 8, "num_predict": 50}
    assert [m["role"] for m in payload["messages"]] == ["system", "user"]


def test_model_override_is_explicit_per_request() -> None:
    post, calls = fake_ollama_post([OK])
    result = OllamaText("http://x", "qwen3.5:9b", post=post).generate_json(
        TextRequest(prompt="p", output=Reply, model="qwen3:4b")
    )
    assert calls[0]["payload"]["model"] == result.model == "qwen3:4b"


def test_usage_is_converted_from_nanoseconds() -> None:
    post, _ = fake_ollama_post([OK])
    provider = OllamaText("http://x", "m", post=post)
    usage = provider.generate_json(TextRequest(prompt="p", output=Reply)).usage
    assert (usage.input_tokens, usage.output_tokens) == (120, 30)
    assert (usage.duration_ms, usage.load_ms, usage.prompt_ms, usage.generation_ms) == (3000, 1000, 1500, 500)
    assert usage.cached_input_tokens == 0


def failing_post(status: int | None) -> Any:
    def post(url: str, payload: Mapping[str, Any], timeout: float) -> dict[str, Any]:
        raise TransportError(status, "falhou")

    return post


def test_missing_model_is_model_unavailable() -> None:
    with pytest.raises(ModelUnavailable, match="ollama pull qwen9"):
        OllamaText("http://x", "qwen9", post=failing_post(404)).generate_json(REQUEST)


def test_connection_failure_is_provider_error() -> None:
    with pytest.raises(ProviderError) as error:
        OllamaText("http://x", "m", post=failing_post(None)).generate_json(REQUEST)
    assert error.value.reason == "provider_error"


def test_truncated_answer_is_invalid_output() -> None:
    post, _ = fake_ollama_post(['{"text": "o'], done_reason="length")
    with pytest.raises(InvalidOutput, match="cortada"):
        OllamaText("http://x", "m", post=post).generate_json(
            TextRequest(prompt="p", output=Reply, max_tokens=5)
        )
