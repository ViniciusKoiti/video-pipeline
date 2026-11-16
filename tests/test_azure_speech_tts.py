"""Adapter Azure Speech (ADR 058) com um POST falso: sem rede (§2.10), sem esperar de verdade."""

from __future__ import annotations

import io
import shutil
import urllib.error
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import pytest

from app.bootstrap import ConfigurationError, build_context
from app.providers.base import ProviderInfo
from app.providers.errors import (
    InvalidOutput,
    ModelUnavailable,
    PaidApiBlocked,
    ProviderError,
    QuotaExhausted,
)
from app.providers.http import TransportError, post_bytes
from app.providers.tts.azure_speech import AzureSpeechTTS, ssml
from app.providers.tts.base import BatchTTS, SpeechRequest, SpeechResult
from app.settings import load_settings, speech_chars_per_second
from app.settings.constants.settings_constants import SettingsConstants
from tests.test_gemini_tts import FakeClock, wav_bytes

REPO_ROOT = Path(__file__).resolve().parents[1]
KEY = "chave-secreta"
ENV = {"AZURE_SPEECH_KEY": KEY, "AZURE_SPEECH_REGION": "brazilsouth"}
FORMAT = "riff-24khz-16bit-mono-pcm"
NS = "{http://www.w3.org/2001/10/synthesis}"


class FakePost:
    """Devolve as respostas em ordem; `TransportError` na lista é levantado. Guarda o que foi enviado."""

    def __init__(self, *replies: bytes | TransportError) -> None:
        self.replies = list(replies)
        self.calls: list[tuple[str, bytes, Mapping[str, str]]] = []

    def __call__(self, url: str, body: bytes, headers: Mapping[str, str], timeout: float) -> bytes:
        self.calls.append((url, body, headers))
        reply = self.replies.pop(0)
        if isinstance(reply, TransportError):
            raise reply
        return reply


def make(post: FakePost, clock: FakeClock | None = None, **extra: Any) -> AzureSpeechTTS:
    clock = clock or FakeClock()
    settings: dict[str, Any] = {
        "voices": {"pt-BR": "pt-BR-AntonioNeural"}, "output_format": FORMAT, "post": post,
        "clock": clock, "sleep": clock.sleep,
    }
    return AzureSpeechTTS(KEY, "brazilsouth", **{**settings, **extra})


def request(tmp_path: Path, text: str = "Em janeiro de 1918.", **extra: Any) -> SpeechRequest:
    return SpeechRequest(text=text, out_path=tmp_path / "voice" / "S01.wav", language="pt-BR", **extra)


def test_writes_the_wav_and_sends_ssml_with_the_key_only_in_the_header(tmp_path: Path) -> None:
    post = FakePost(wav_bytes())
    result = make(post).synthesize_speech(request(tmp_path))
    out = tmp_path / "voice" / "S01.wav"
    assert result == SpeechResult(path=out, model="azure-speech-neural", voice="pt-BR-AntonioNeural")
    assert out.read_bytes() == wav_bytes()
    (url, body, headers), = post.calls
    assert url == "https://brazilsouth.tts.speech.microsoft.com/cognitiveservices/v1"
    assert headers == {
        "Ocp-Apim-Subscription-Key": KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": FORMAT,
    }
    assert KEY not in url and KEY.encode() not in body
    root = ElementTree.fromstring(body.decode())
    assert root.tag == f"{NS}speak" and root.attrib["version"] == "1.0"
    assert root.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "pt-BR"
    voice = root.find(f"{NS}voice")
    assert voice is not None and voice.attrib == {"name": "pt-BR-AntonioNeural"}
    assert voice.text == "Em janeiro de 1918." and len(voice) == 0  # sem prosody nem break


def test_the_text_is_escaped_for_ssml() -> None:
    text = "Tom & Jerry <b>disse</b> \"oi\" e 'tchau' > 3"
    document = ssml(text, language="pt-BR", voice="pt-BR-AntonioNeural", rate=1.0, pause_ms=500)
    assert "&amp; Jerry &lt;b&gt;disse&lt;/b&gt; &quot;oi&quot; e &apos;tchau&apos; &gt; 3" in document
    voice = ElementTree.fromstring(document).find(f"{NS}voice")
    assert voice is not None and voice.text == text and len(voice) == 0  # nenhuma tag veio do texto


def test_a_voice_name_cannot_break_out_of_the_attribute() -> None:
    document = ssml("Oi.", language="pt-BR", voice='x"><break time="20s"/>', rate=1.0, pause_ms=500)
    voice = ElementTree.fromstring(document).find(f"{NS}voice")
    assert voice is not None and voice.attrib["name"] == 'x"><break time="20s"/>' and len(voice) == 0


def test_short_pause_becomes_a_real_break_and_rate_becomes_prosody(tmp_path: Path) -> None:
    post = FakePost(wav_bytes(), wav_bytes())
    text = "Primeiro. <short pause> Depois & fim."
    make(post, pause_ms=700).synthesize_speech(request(tmp_path, text))
    body = post.calls[0][1].decode()
    assert "short pause" not in body
    assert '>Primeiro.<break time="700ms"/>Depois &amp; fim.</voice>' in body
    make(post, rate=0.9).synthesize_speech(request(tmp_path, text))
    slower = ElementTree.fromstring(post.calls[1][1].decode()).find(f"{NS}voice/{NS}prosody")
    assert slower is not None and slower.attrib == {"rate": "0.9"}
    assert [child.tag for child in slower] == [f"{NS}break"]


def test_fingerprint_has_the_effective_parameters_and_not_the_text(tmp_path: Path) -> None:
    plain, pause = request(tmp_path), request(tmp_path, "Um. <short pause> Dois.")
    tts = make(FakePost())
    assert tts.identity == "azure_speech" and tts.info == ProviderInfo("azure_speech", remote=True)
    assert tts.fingerprint(plain) == f"azure_speech|pt-BR-AntonioNeural|{FORMAT}"
    assert tts.fingerprint(plain) == tts.fingerprint(request(tmp_path, "Outro texto."))
    assert tts.fingerprint(pause) == f"azure_speech|pt-BR-AntonioNeural|{FORMAT}|pausa500"
    assert make(FakePost(), pause_ms=700).fingerprint(plain) == tts.fingerprint(plain)  # sem pausa no texto
    assert make(FakePost(), pause_ms=700).fingerprint(pause).endswith("|pausa700")
    assert make(FakePost(), rate=0.9).fingerprint(pause).endswith(f"|{FORMAT}|rate0.9|pausa500")
    other_format = make(FakePost(), output_format="riff-48khz-16bit-mono-pcm")
    assert other_format.fingerprint(plain) != tts.fingerprint(plain)
    assert tts.fingerprint(request(tmp_path, voice="pt-BR-FranciscaNeural")) != tts.fingerprint(plain)
    assert tts.fingerprint(request(tmp_path, delivery="hook")) == tts.fingerprint(plain)  # sem fator, igual


def test_the_delivery_factor_multiplies_the_rate_in_the_ssml_and_the_identity(tmp_path: Path) -> None:
    post = FakePost(wav_bytes(), wav_bytes())
    tts = make(post, rate=1.05, delivery_rates={"calm": 0.9, "hook": 1.06})
    neutral = request(tmp_path)
    assert tts.rate_for(neutral) == 1.05 and tts.rate_for(request(tmp_path, delivery="turn")) == 1.05
    assert tts.rate_for(request(tmp_path, delivery="calm")) == 0.945
    assert tts.fingerprint(neutral) == make(FakePost(), rate=1.05).fingerprint(neutral)  # o nome de antes
    assert tts.fingerprint(request(tmp_path, delivery="calm")).endswith(f"|{FORMAT}|rate0.945")
    assert tts.fingerprint(request(tmp_path, delivery="hook")).endswith("|rate1.113")
    tts.synthesize_speech(request(tmp_path, delivery="calm"))
    prosody = ElementTree.fromstring(post.calls[0][1].decode()).find(f"{NS}voice/{NS}prosody")
    assert prosody is not None and prosody.attrib == {"rate": "0.945"}
    calm_at_one = make(post, delivery_rates={"calm": 1.0})
    calm_at_one.synthesize_speech(request(tmp_path, delivery="calm"))
    assert "prosody" not in post.calls[1][1].decode()  # velocidade efetiva 1: sem a tag


def test_an_effective_rate_outside_the_service_range_leaves_the_scene_pending(tmp_path: Path) -> None:
    tts = make(FakePost(), rate=1.9, delivery_rates={"hook": 1.2})
    with pytest.raises(ProviderError, match="fora de 0.5 a 2"):
        tts.fingerprint(request(tmp_path, delivery="hook"))


def test_the_delivery_factors_are_validated_in_the_settings(tmp_path: Path) -> None:
    from app.settings.models.azure_speech_settings import AzureSpeechSettings

    assert AzureSpeechSettings(delivery={"calm": 0.9}).delivery == {"calm": 0.9}
    with pytest.raises(ValueError, match="fora de 0.7 a 1.3: hook"):
        AzureSpeechSettings(delivery={"hook": 1.5})
    with pytest.raises(ValueError):
        AzureSpeechSettings(delivery={"sussurro": 0.9})


def test_calls_are_spaced_to_the_free_tier_limit(tmp_path: Path) -> None:
    clock = FakeClock()
    tts = make(FakePost(wav_bytes(), wav_bytes()), clock)
    tts.synthesize_speech(request(tmp_path))
    clock.now += 1
    tts.synthesize_speech(request(tmp_path))
    assert clock.slept == [pytest.approx(2.5)]  # 60 / 20 + 0,5 s de folga, menos 1 s que já passou


def test_one_rate_limit_is_retried_and_a_second_becomes_quota_exhausted(tmp_path: Path) -> None:
    limit = TransportError(429, f"Too many requests {KEY}")
    post = FakePost(limit, wav_bytes())
    assert make(post).synthesize_speech(request(tmp_path)).voice == "pt-BR-AntonioNeural"
    assert len(post.calls) == 2
    with pytest.raises(QuotaExhausted, match="Too many requests") as raised:
        make(FakePost(limit, limit)).synthesize_speech(request(tmp_path))
    assert KEY not in str(raised.value)  # mesmo se o serviço a devolvesse no corpo do erro


@pytest.mark.parametrize("status", [500, 502, 503, None])  # None: tempo esgotado ou rede
def test_passing_failures_are_retried_once(tmp_path: Path, status: int | None) -> None:
    busy = TransportError(status, "indisponível")
    assert make(FakePost(busy, wav_bytes())).synthesize_speech(request(tmp_path)).path.is_file()
    with pytest.raises(ProviderError) as raised:
        make(FakePost(busy, busy)).synthesize_speech(request(tmp_path / "b"))
    assert not isinstance(raised.value, QuotaExhausted)


@pytest.mark.parametrize(
    ("reply", "error", "message"),
    [
        (TransportError(401, "Unauthorized"), ProviderError, "AZURE_SPEECH_KEY e AZURE_SPEECH_REGION"),
        (TransportError(403, "Forbidden"), ProviderError, "chave ou região recusada"),
        (TransportError(400, "Bad request"), ProviderError, "Bad request"),
        (b"<html>erro</html>", InvalidOutput, "sem cabeçalho WAV"),
        (b"RIFF", InvalidOutput, "não é um WAV válido"),
    ],
)
def test_failures_become_provider_errors_and_publish_nothing(
    tmp_path: Path, reply: Any, error: type[Exception], message: str
) -> None:
    post = FakePost(reply)
    with pytest.raises(error, match=message) as raised:
        make(post).synthesize_speech(request(tmp_path))
    assert KEY not in str(raised.value) and len(post.calls) == 1  # sem nova tentativa
    assert not list(tmp_path.rglob("*.wav"))


def test_a_failed_call_keeps_the_previous_wav(tmp_path: Path) -> None:
    out = tmp_path / "voice" / "S01.wav"
    out.parent.mkdir()
    out.write_bytes(wav_bytes(480))
    with pytest.raises(ProviderError):
        make(FakePost(TransportError(400, "erro"))).synthesize_speech(request(tmp_path))
    assert out.read_bytes() == wav_bytes(480) and [p.name for p in out.parent.iterdir()] == ["S01.wav"]


def test_missing_voice_empty_and_huge_text_are_refused(tmp_path: Path) -> None:
    post = FakePost()
    english = SpeechRequest(text="Hi.", out_path=tmp_path / "a.wav", language="en")
    for call in (make(post).synthesize_speech, make(post).fingerprint):
        with pytest.raises(ModelUnavailable, match="sem voz"):
            call(english)
    with pytest.raises(ProviderError, match="nenhum texto"):
        make(post).synthesize_speech(request(tmp_path, "  "))
    with pytest.raises(ProviderError, match="5000 caracteres"):
        make(post).synthesize_speech(request(tmp_path, "a" * 5001))
    assert post.calls == []  # nada foi enviado
    assert not isinstance(make(post), BatchTTS)  # uma fala por chamada


# --- Composição: chave, região, custo zero ------------------------------------------------------


def test_the_voice_is_registered_by_name_and_the_defaults_stay(tmp_path: Path) -> None:
    settings = load_settings(REPO_ROOT, environ=ENV)
    assert (settings.providers.tts, settings.providers.tts_final) == ("kokoro", "chatterbox_modal")
    assert settings.azure_speech.voices["pt-BR"] == "pt-BR-AntonioNeural"
    assert settings.azure_speech.tier == "F0" and settings.azure_speech.output_format == FORMAT
    assert KEY not in repr(settings)
    assert speech_chars_per_second(settings) == settings.chatterbox.chars_per_second  # a voz final não mudou
    tts = build_context(REPO_ROOT, environ=ENV).tts_named("azure_speech")
    assert tts.info == ProviderInfo("azure_speech", remote=True)  # custo zero: §2.1
    rate = settings.azure_speech.rate  # a velocidade é do providers.toml; o rótulo só aparece fora de 1
    suffix = f"|rate{rate:g}" if rate != 1.0 else ""
    assert tts.fingerprint(request(tmp_path)) == f"azure_speech|pt-BR-AntonioNeural|{FORMAT}{suffix}"


@pytest.mark.parametrize(
    ("environ", "message"),
    [
        ({}, "AZURE_SPEECH_KEY ausente no .env"),
        ({"AZURE_SPEECH_REGION": "brazilsouth"}, "AZURE_SPEECH_KEY ausente no .env"),
        ({"AZURE_SPEECH_KEY": KEY}, "AZURE_SPEECH_REGION ausente no .env"),
        ({"AZURE_SPEECH_KEY": KEY, "AZURE_SPEECH_REGION": "evil.example/x?"}, "AZURE_SPEECH_REGION inválida"),
    ],
)
def test_without_key_or_region_the_error_says_what_is_missing(
    environ: dict[str, str], message: str, tmp_path: Path
) -> None:
    # raiz sem `.env`: a chave real do dono no `.env` do repositório não pode vazar para o teste
    shutil.copytree(REPO_ROOT / "config", tmp_path / "config")
    context = build_context(tmp_path, environ=environ)  # as outras vozes seguem funcionando sem a chave
    with pytest.raises(ConfigurationError, match=message) as raised:
        context.tts_named("azure_speech")
    assert KEY not in str(raised.value)


def test_a_paid_tier_is_blocked_by_the_zero_cost_rule(tmp_path: Path) -> None:
    config = (REPO_ROOT / SettingsConstants.CONFIG_FILE).read_text()
    assert 'tier = "F0"' in config
    (tmp_path / SettingsConstants.CONFIG_FILE.parent).mkdir()
    (tmp_path / SettingsConstants.CONFIG_FILE).write_text(config.replace('tier = "F0"', 'tier = "S0"'))
    with pytest.raises(PaidApiBlocked, match="ALLOW_PAID_API=false"):
        build_context(tmp_path, environ=ENV).tts_named("azure_speech")


# --- Transporte: corpo e resposta em bytes, erro sem URL nem cabeçalho ---------------------------


def test_post_bytes_sends_the_body_and_returns_the_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[Any] = []

    def urlopen(sent: Any, timeout: float) -> io.BytesIO:
        seen.append(sent)
        return io.BytesIO(b"RIFFdados")

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    assert post_bytes("https://example.invalid/v1", b"<speak/>", {"X-Chave": KEY}, 5) == b"RIFFdados"
    assert seen[0].data == b"<speak/>" and seen[0].get_method() == "POST"
    assert seen[0].get_header("X-chave") == KEY and seen[0].get_header("User-agent")


def test_post_bytes_errors_carry_no_url_and_no_header(monkeypatch: pytest.MonkeyPatch) -> None:
    def urlopen(sent: Any, timeout: float) -> io.BytesIO:
        raise urllib.error.HTTPError(sent.full_url, 429, "Too Many", {}, io.BytesIO(b"quota"))  # type: ignore[arg-type]

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    with pytest.raises(TransportError) as raised:
        post_bytes("https://example.invalid/v1", b"x", {"X-Chave": KEY}, 5)
    assert raised.value.status == 429 and str(raised.value) == "HTTP 429: quota"


def test_phoneme_glossary_wraps_each_whole_word_in_ipa(tmp_path: Path) -> None:
    post = FakePost(wav_bytes())
    lexicon = {"TotalPass": "ˌtɔ.taw.ˈpas", "Total": "ˈto.taw"}
    text = "O TotalPass cresceu. <short pause> TotalPass México & Total, não TotalPassX."
    tts = make(post)
    assert tts.phoneme_alphabet == "ipa"
    tts.synthesize_speech(request(tmp_path, text, lexicon=lexicon))
    voice = ElementTree.fromstring(post.calls[0][1].decode()).find(f"{NS}voice")
    assert voice is not None
    phonemes = [(p.attrib, p.text) for p in voice.iter(f"{NS}phoneme")]
    assert phonemes == [
        ({"alphabet": "ipa", "ph": "ˌtɔ.taw.ˈpas"}, "TotalPass"),
        ({"alphabet": "ipa", "ph": "ˌtɔ.taw.ˈpas"}, "TotalPass"),
        ({"alphabet": "ipa", "ph": "ˈto.taw"}, "Total"),
    ]
    assert "TotalPassX" in "".join(voice.itertext())  # palavra maior não é trocada


def test_fingerprint_counts_only_the_phoneme_terms_in_the_text(tmp_path: Path) -> None:
    tts = make(FakePost())
    plain = request(tmp_path, "Sem marca nenhuma.")
    with_term = request(tmp_path, "O TotalPass cresceu.", lexicon={"TotalPass": "ˌtɔ.taw.ˈpas"})
    other_ipa = request(tmp_path, "O TotalPass cresceu.", lexicon={"TotalPass": "ˈtɔ.taw.ˌpas"})
    unused = request(tmp_path, "Sem marca nenhuma.", lexicon={"TotalPass": "ˌtɔ.taw.ˈpas"})
    assert tts.fingerprint(unused) == tts.fingerprint(plain) == f"azure_speech|pt-BR-AntonioNeural|{FORMAT}"
    assert "|ipa" in tts.fingerprint(with_term)
    assert tts.fingerprint(with_term) != tts.fingerprint(other_ipa)
