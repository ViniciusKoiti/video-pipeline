"""Adapter do Whisper da Groq (ADR 023) com transporte falso: o que vai na requisição e como as falhas viram
erros de provedor. Sem rede."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from app.providers.alignment.base import TimedWord
from app.providers.alignment.groq import PROMPT_CHARS, URL, GroqWordAligner
from app.providers.errors import InvalidOutput, ModelUnavailable, ProviderError, QuotaExhausted
from app.providers.http import TransportError


class FakePost:
    def __init__(self, reply: dict[str, Any] | TransportError) -> None:
        self.reply = reply
        self.calls: list[tuple[str, Mapping[str, str], Mapping[str, Path], Mapping[str, str]]] = []

    def __call__(
        self, url: str, fields: Mapping[str, str], files: Mapping[str, Path], headers: Mapping[str, str],
        timeout: float,
    ) -> dict[str, Any]:
        self.calls.append((url, dict(fields), dict(files), dict(headers)))
        if isinstance(self.reply, TransportError):
            raise self.reply
        return self.reply


def aligner(reply: dict[str, Any] | TransportError) -> tuple[GroqWordAligner, FakePost]:
    post = FakePost(reply)
    return GroqWordAligner("chave-secreta", model="whisper-large-v3-turbo", post=post), post


def test_request_asks_for_words_in_the_episode_language(tmp_path: Path) -> None:
    audio = tmp_path / "S01.wav"
    audio.write_bytes(b"RIFF")
    provider, post = aligner({"words": [{"word": " Meia", "start": 0.12, "end": 0.4},
                                        {"word": "lata.", "start": 0.45, "end": 0.9}]})
    words = provider.recognize_words(audio, "pt-BR", prompt="x" * (PROMPT_CHARS + 50))
    assert words == [TimedWord("Meia", 120, 400), TimedWord("lata.", 450, 900)]
    ((url, fields, files, headers),) = post.calls
    assert url == URL and "chave" not in url
    assert fields["language"] == "pt" and fields["timestamp_granularities[]"] == "word"
    assert fields["response_format"] == "verbose_json" and fields["model"] == "whisper-large-v3-turbo"
    assert len(fields["prompt"]) == PROMPT_CHARS
    assert files == {"file": audio} and headers == {"Authorization": "Bearer chave-secreta"}
    assert provider.info.remote and provider.info.usd_per_call == 0


@pytest.mark.parametrize(
    ("error", "kind"),
    [
        (TransportError(429, "rate limit"), QuotaExhausted),
        (TransportError(404, "model not found"), ModelUnavailable),
        (TransportError(500, "erro"), ProviderError),
        (TransportError(None, "sem rede"), ProviderError),
    ],
)
def test_transport_failures_become_provider_errors(
    tmp_path: Path, error: TransportError, kind: type[ProviderError]
) -> None:
    provider, _ = aligner(error)
    with pytest.raises(kind):
        provider.recognize_words(tmp_path / "S01.wav", "pt-BR")


@pytest.mark.parametrize("reply", [{}, {"words": []}, {"words": [{"word": "a"}]}])
def test_a_reply_without_timed_words_is_invalid(tmp_path: Path, reply: dict[str, Any]) -> None:
    provider, _ = aligner(reply)
    with pytest.raises(InvalidOutput):
        provider.recognize_words(tmp_path / "S01.wav", "pt-BR")


def test_multipart_body_carries_fields_and_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import io
    import json as json_module
    import urllib.request

    from app.providers import http

    audio = tmp_path / "S01.wav"
    audio.write_bytes(b"RIFF-dados")
    seen: dict[str, Any] = {}

    def fake_urlopen(request: urllib.request.Request, timeout: float) -> io.BytesIO:
        seen["body"], seen["type"] = request.data, request.headers["Content-type"]
        return io.BytesIO(json_module.dumps({"ok": True}).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert http.post_multipart("https://x", {"model": "m"}, {"file": audio}, {}, 5) == {"ok": True}
    boundary = seen["type"].split("boundary=")[1]
    assert seen["body"].startswith(f"--{boundary}".encode())
    assert seen["body"].endswith(f"--{boundary}--\r\n".encode())
    assert b'name="model"\r\n\r\nm\r\n' in seen["body"]
    assert b'filename="S01.wav"\r\nContent-Type: audio/x-wav\r\n\r\nRIFF-dados\r\n' in seen["body"]
