"""Adapter Gemini TTS (ADR 012) com um POST falso: sem rede (§2.10), sem esperar de verdade."""

from __future__ import annotations

import base64
import io
import wave
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from app.bootstrap import build_context
from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput, ModelUnavailable, ProviderError, QuotaExhausted
from app.providers.http import TransportError
from app.providers.tts.base import SpeechRequest, SpeechResult
from app.providers.tts.gemini import API, GeminiTTS
from app.settings import CONFIG_FILE, load_settings, speech_chars_per_second

REPO_ROOT = Path(__file__).resolve().parents[1]
STYLE = "narração de documentário"


def wav_bytes(frames: int = 2400) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(b"\x00\x00" * frames)
    return buffer.getvalue()


def audio_response(data: bytes) -> dict[str, Any]:
    return {"steps": [
        {"type": "user_input"},
        {"type": "model_output", "content": [{"type": "audio", "data": base64.b64encode(data).decode()}]},
    ]}


class FakePost:
    """Devolve as respostas em ordem; `TransportError` na lista é levantado. Guarda o que foi enviado."""

    def __init__(self, *replies: dict[str, Any] | TransportError) -> None:
        self.replies = list(replies)
        self.calls: list[tuple[str, Mapping[str, Any], Mapping[str, str]]] = []

    def __call__(self, url: str, body: Mapping[str, Any], headers: Mapping[str, str], timeout: float) -> Any:
        self.calls.append((url, body, headers))
        reply = self.replies.pop(0)
        if isinstance(reply, TransportError):
            raise reply
        return reply


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0
        self.slept: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


def make(post: FakePost, clock: FakeClock | None = None, rpm: int = 3) -> GeminiTTS:
    clock = clock or FakeClock()
    return GeminiTTS(
        "chave-secreta", model="gemini-3.8-flash-tts", voices={"pt-BR": "Charon"}, styles={"pt-BR": STYLE},
        requests_per_minute=rpm, post=post, clock=clock, sleep=clock.sleep,
    )


def request(tmp_path: Path, **extra: Any) -> SpeechRequest:
    out = tmp_path / "voice" / "S01.wav"
    return SpeechRequest(text="Em janeiro de 1918.", out_path=out, language="pt-BR", **extra)


def test_writes_the_wav_and_sends_voice_and_style_without_the_key_in_the_body(tmp_path: Path) -> None:
    post = FakePost(audio_response(wav_bytes()))
    result = make(post).synthesize_speech(request(tmp_path))
    out = tmp_path / "voice" / "S01.wav"
    assert result == SpeechResult(path=out, model="gemini-3.8-flash-tts", voice="Charon")
    assert result.path.read_bytes() == wav_bytes()
    (url, body, headers), = post.calls
    assert url == API and headers == {"x-goog-api-key": "chave-secreta"}
    assert "chave-secreta" not in repr(body)
    content = body["input"][0]["content"][0]
    assert content["text"] == "Em janeiro de 1918."  # o texto vai ao pé da letra
    assert content["annotations"] == [{"type": "speech_metadata", "style": STYLE}]
    assert body["generation_config"] == {"speech_config": [{"voice": "Charon"}]}


def test_calls_are_spaced_to_the_free_tier_limit(tmp_path: Path) -> None:
    clock = FakeClock()
    post = FakePost(*(audio_response(wav_bytes()) for _ in range(3)))
    tts = make(post, clock)
    tts.synthesize_speech(request(tmp_path))
    clock.now += 5  # a segunda fala chega 5 s depois
    tts.synthesize_speech(request(tmp_path))
    tts.synthesize_speech(request(tmp_path))
    assert clock.slept == [pytest.approx(16.0), pytest.approx(21.0)]  # 60 / 3 + 1 s de folga


def test_one_rate_limit_is_retried_and_a_second_becomes_quota_exhausted(tmp_path: Path) -> None:
    limit = TransportError(429, '{"error": "Rate limit exceeded"}')
    post = FakePost(limit, audio_response(wav_bytes()))
    assert make(post).synthesize_speech(request(tmp_path)).voice == "Charon"
    assert len(post.calls) == 2
    with pytest.raises(QuotaExhausted):
        make(FakePost(limit, limit)).synthesize_speech(request(tmp_path))


@pytest.mark.parametrize(
    ("reply", "error"),
    [
        (TransportError(404, "not found"), ModelUnavailable),
        (TransportError(500, "internal"), ProviderError),
        ({"steps": [{"type": "model_output", "content": []}]}, InvalidOutput),
        (audio_response(b"not a wav"), InvalidOutput),
    ],
)
def test_failures_become_provider_errors(tmp_path: Path, reply: Any, error: type[Exception]) -> None:
    with pytest.raises(error) as raised:
        make(FakePost(reply)).synthesize_speech(request(tmp_path))
    assert "chave-secreta" not in str(raised.value)


def test_missing_voice_and_phoneme_glossary_are_refused(tmp_path: Path) -> None:
    with pytest.raises(ModelUnavailable, match="sem voz"):
        english = SpeechRequest(text="Hi.", out_path=tmp_path / "a.wav", language="en")
        make(FakePost()).synthesize_speech(english)
    with pytest.raises(ProviderError, match="glossário"):
        make(FakePost()).synthesize_speech(request(tmp_path, lexicon={"Ignácio": "iɡnˈasju"}))


def test_config_picks_gemini_with_the_key_from_env_and_its_speech_rate() -> None:
    settings = load_settings(REPO_ROOT, environ={"GEMINI_API_KEY": "chave"})
    assert settings.providers.tts == "gemini" and settings.gemini_tts.voices["pt-BR"] == "Charon"
    assert speech_chars_per_second(settings) == settings.gemini_tts.chars_per_second
    context = build_context(REPO_ROOT, environ={"GEMINI_API_KEY": "chave"})
    assert context.tts.info == ProviderInfo("gemini_tts", remote=True)  # custo zero: passa pela trava (§2.1)


def test_kokoro_is_one_line_away(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / CONFIG_FILE).parent.mkdir(parents=True)
    config = (REPO_ROOT / CONFIG_FILE).read_text().replace('tts = "gemini"', 'tts = "kokoro"', 1)
    (root / CONFIG_FILE).write_text(config)
    settings = load_settings(root, environ={})
    assert speech_chars_per_second(settings) == settings.kokoro.chars_per_second
