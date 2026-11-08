"""Transporte preserva objetos/listas e recusa escalares, sem rede nem dados de resposta em erros."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from app.providers.alignment.groq import GroqWordAligner
from app.providers.errors import InvalidOutput
from app.providers.http import get_json, parse_json, post_json_with_headers, post_multipart
from app.providers.text.base import TextRequest
from app.providers.text.ollama import OllamaText
from app.providers.tts.base import SpeechRequest
from app.providers.tts.gemini import GeminiTTS


@pytest.mark.parametrize("payload", [{"ok": True}, [{"id": "item"}]])
@pytest.mark.parametrize("method", ["get", "post", "multipart"])
def test_transports_preserve_top_level_json_shape(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, payload: object, method: str
) -> None:
    class Response(io.BytesIO):
        headers: dict[str, str] = {}

    def urlopen(*args: Any, **kwargs: Any) -> Response:
        return Response(json.dumps(payload).encode())

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    if method == "get":
        actual = get_json("https://example.invalid", {}, 1).data
    elif method == "post":
        actual = post_json_with_headers("https://example.invalid", {}, {}, 1)
    else:
        media = tmp_path / "voice.wav"
        media.write_bytes(b"audio")
        actual = post_multipart("https://example.invalid", {}, {"file": media}, {}, 1)
    assert actual == payload


@pytest.mark.parametrize("payload", [None, True, 42, "token-privado"])
def test_json_scalar_is_rejected_without_echoing_the_content(payload: object) -> None:
    with pytest.raises(ValueError, match="objeto ou uma lista") as caught:
        parse_json(json.dumps(payload))
    assert "token-privado" not in str(caught.value)


@pytest.mark.parametrize("provider", ["ollama", "gemini", "groq"])
def test_providers_convert_invalid_json_to_scene_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, provider: str
) -> None:
    def urlopen(*args: Any, **kwargs: Any) -> io.BytesIO:
        return io.BytesIO(b'"token-privado"')

    class Reply(BaseModel):
        text: str

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    with pytest.raises(InvalidOutput, match="JSON inválida") as caught:
        if provider == "ollama":
            OllamaText("https://example.invalid", "test").generate_json(TextRequest(prompt="x", output=Reply))
        elif provider == "gemini":
            gemini = GeminiTTS("key", model="test", voices={"en": "test"}, styles={}, requests_per_minute=3)
            gemini.synthesize_speech(SpeechRequest(text="x", out_path=tmp_path / "out.wav"))
        else:
            audio = tmp_path / "in.wav"
            audio.write_bytes(b"audio")
            GroqWordAligner("key", model="test").recognize_words(audio, "en")
    assert "token-privado" not in str(caught.value)
    assert not (tmp_path / "out.wav").exists()
