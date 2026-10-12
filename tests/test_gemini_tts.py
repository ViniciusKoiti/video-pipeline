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
from app.providers.tts.gemini import API, SCENE_BREAK, TIMEOUT_S, GeminiTTS
from app.settings import CONFIG_FILE, load_settings, speech_chars_per_second
from tests.test_pauses import THREE_SCENES, narration

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
        self.timeouts: list[float] = []

    def __call__(self, url: str, body: Mapping[str, Any], headers: Mapping[str, str], timeout: float) -> Any:
        self.calls.append((url, body, headers))
        self.timeouts.append(timeout)
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
    with pytest.raises(QuotaExhausted, match="Rate limit exceeded") as raised:
        make(FakePost(limit, limit)).synthesize_speech(request(tmp_path))
    assert "chave-secreta" not in str(raised.value)


@pytest.mark.parametrize("status", [503, 500, None])  # None: tempo esgotado ou rede
def test_passing_failures_are_retried_once(tmp_path: Path, status: int | None) -> None:
    busy = TransportError(status, "high demand")
    assert make(FakePost(busy, audio_response(wav_bytes()))).synthesize_speech(request(tmp_path)).voice
    with pytest.raises(ProviderError) as raised:
        make(FakePost(busy, busy)).synthesize_speech(request(tmp_path))
    assert not isinstance(raised.value, QuotaExhausted)


@pytest.mark.parametrize(
    ("reply", "error"),
    [
        (TransportError(404, "not found"), ModelUnavailable),
        (TransportError(400, "bad request"), ProviderError),
        ({"steps": [{"type": "model_output", "content": []}]}, InvalidOutput),
        (audio_response(b"not a wav"), InvalidOutput),
    ],
)
def test_failures_become_provider_errors(tmp_path: Path, reply: Any, error: type[Exception]) -> None:
    post = FakePost(reply)
    with pytest.raises(error) as raised:
        make(post).synthesize_speech(request(tmp_path))
    assert "chave-secreta" not in str(raised.value) and len(post.calls) == 1  # sem nova tentativa


def test_missing_voice_and_phoneme_glossary_are_refused(tmp_path: Path) -> None:
    with pytest.raises(ModelUnavailable, match="sem voz"):
        english = SpeechRequest(text="Hi.", out_path=tmp_path / "a.wav", language="en")
        make(FakePost()).synthesize_speech(english)
    with pytest.raises(ProviderError, match="glossário"):
        make(FakePost()).synthesize_speech(request(tmp_path, lexicon={"Ignácio": "iɡnˈasju"}))


def test_gemini_is_still_a_voice_by_name_after_the_cloned_voice_became_the_final_one() -> None:
    settings = load_settings(REPO_ROOT, environ={"GEMINI_API_KEY": "chave"})
    assert settings.providers.tts_final == "chatterbox"  # ADR 016; a Charon fica para o vídeo-régua
    assert settings.gemini_tts.voices["pt-BR"] == "Charon"
    context = build_context(REPO_ROOT, environ={"GEMINI_API_KEY": "chave"})
    assert context.tts.info.name == "kokoro"
    assert context.tts_named("gemini").info == ProviderInfo("gemini_tts", remote=True)  # custo zero: §2.1


def test_check_estimates_with_the_gemini_rate_when_it_is_the_final_voice(tmp_path: Path) -> None:
    config = (REPO_ROOT / CONFIG_FILE).read_text().replace('tts_final = "chatterbox"', 'tts_final = "gemini"')
    (tmp_path / CONFIG_FILE.parent).mkdir()
    (tmp_path / CONFIG_FILE).write_text(config)
    settings = load_settings(tmp_path, {})
    assert settings.providers.tts_final == "gemini"
    assert speech_chars_per_second(settings) == settings.gemini_tts.chars_per_second


def test_without_a_final_voice_the_draft_voice_is_used(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / CONFIG_FILE).parent.mkdir(parents=True)
    lines = (REPO_ROOT / CONFIG_FILE).read_text().splitlines()
    (root / CONFIG_FILE).write_text("\n".join(line for line in lines if not line.startswith("tts_final")))
    settings = load_settings(root, environ={})
    assert settings.providers.tts_final is None
    assert speech_chars_per_second(settings) == settings.kokoro.chars_per_second
    context = build_context(root, environ={})
    assert context.tts_final is context.tts


def test_the_daily_limit_is_not_retried(tmp_path: Path) -> None:
    daily = TransportError(429, "Rate limit exceeded (limit: 10 requests per day on Free Tier)")
    post = FakePost(daily)
    with pytest.raises(QuotaExhausted, match="per day"):
        make(post).synthesize_speech(request(tmp_path))
    assert len(post.calls) == 1  # a segunda chamada só gastaria cota


# --- Várias cenas por chamada -------------------------------------------------------------------


def scene_requests(tmp_path: Path, texts: list[str], language: str = "pt-BR") -> list[SpeechRequest]:
    return [SpeechRequest(text=text, out_path=tmp_path / "voice" / f"S0{i}.wav", language=language)
            for i, text in enumerate(texts, start=1)]


def test_several_scenes_go_in_one_call_and_come_back_cut(tmp_path: Path) -> None:
    audio = narration(tmp_path / "lote.wav", THREE_SCENES).read_bytes()
    post = FakePost(audio_response(audio))
    requests = scene_requests(tmp_path, ["Primeira cena.", "Segunda cena.", "Terceira cena."])
    results = make(post).synthesize_many(requests)
    assert [r.path for r in results] == [r.out_path for r in requests]
    assert all(r.path.is_file() and r.voice == "Charon" for r in results)
    (_, body, _), = post.calls
    assert body["input"][0]["content"][0]["text"] == SCENE_BREAK.join(r.text for r in requests)
    assert post.timeouts[0] > TIMEOUT_S  # lote demora mais que uma fala
    assert not list((tmp_path / "voice").glob("tmp*"))  # o arquivo do lote não fica para trás


def test_a_batch_that_cannot_be_cut_is_invalid_output(tmp_path: Path) -> None:
    audio = narration(tmp_path / "corrido.wav", [("tom", 2.0)]).read_bytes()
    requests = scene_requests(tmp_path, ["Uma.", "Duas."])
    with pytest.raises(InvalidOutput, match="lote de 2 cenas"):
        make(FakePost(audio_response(audio))).synthesize_many(requests)


def test_one_scene_is_a_plain_call_and_mixed_languages_are_refused(tmp_path: Path) -> None:
    post = FakePost(audio_response(wav_bytes()))
    assert len(make(post).synthesize_many(scene_requests(tmp_path, ["Só uma."]))) == 1
    tts = GeminiTTS("chave", model="m", voices={"pt-BR": "Charon", "en": "Charon"}, styles={},
                    requests_per_minute=3, post=FakePost())
    mixed = scene_requests(tmp_path, ["Uma."]) + scene_requests(tmp_path / "en", ["Two."], language="en")
    with pytest.raises(ProviderError, match="um idioma só"):
        tts.synthesize_many(mixed)
