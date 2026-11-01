"""RF3: identidade do cache de voz. Os nomes de WAV de hoje continuam valendo, e a única chave que muda é a
da entrega não neutra do Chatterbox (que antes não levava os valores): mudança declarada na ADR 041.

O oráculo são as funções reais dos scripts (`voice_fingerprint`, `long_speech_tag`, `wav_name`)."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from app.providers.errors import ModelUnavailable, ProviderError
from app.providers.tts.base import SpeechRequest
from app.providers.tts.chatterbox import ChatterboxTTS, reference_hash
from app.providers.tts.constants.chatterbox_constants import ChatterboxConstants
from app.providers.tts.gemini import GeminiTTS
from app.providers.tts.kokoro import KokoroTTS
from app.settings import Settings
from scripts.provisorio.montar_episodio import long_speech_tag, voice_fingerprint
from scripts.provisorio.shorts_tec import Line, wav_name
from tests.fakes import make_settings
from tests.test_chatterbox_tts import make_tts as make_chatterbox
from tests.test_gemini_tts import FakePost, audio_response, wav_bytes

PAUSE = "Primeiro. <short pause> Depois."
PLAIN = "Uma fala simples."
LONG = ("Esta é uma frase razoavelmente longa para encher a fala. " * 8).strip()


def req(text: str = PLAIN, language: str = "pt-BR", **kw: str) -> SpeechRequest:
    return SpeechRequest(text=text, out_path=Path("voice/S01.wav"), language=language, **kw)


def gemini(**kw: object) -> GeminiTTS:
    settings = {
        "model": "gemini-3.8-flash-tts",
        "voices": {"pt-BR": "Charon", "en": "Puck"},
        "styles": {"pt-BR": "narração calma"},
        "requests_per_minute": 3,
        "post": FakePost(audio_response(wav_bytes())),
    }
    return GeminiTTS("chave", **{**settings, **kw})


def long_digest(fingerprint: str, text: str) -> str:
    """O nome de hoje no longo: sha256 do que muda a fala, `|` e o texto."""
    return hashlib.sha256(f"{fingerprint}|{text}".encode()).hexdigest()[:10]


# --- A identidade não é o nome de exibição ------------------------------------------------------


def test_the_cache_identity_is_stable_and_apart_from_the_display_name() -> None:
    assert (GeminiTTS.identity, gemini().info.name) == ("gemini", "gemini_tts")  # alias legado, explícito
    assert KokoroTTS({"en": "am_michael"}).identity == "kokoro"
    local, modal = make_chatterbox(), make_chatterbox(provider="chatterbox_modal", remote=True)
    assert (local.identity, modal.identity) == ("chatterbox", "chatterbox_modal")
    assert local.fingerprint(req()) != modal.fingerprint(req())  # o mesmo texto, outro lugar: outro arquivo


# --- Os nomes de hoje ---------------------------------------------------------------------------


@pytest.mark.parametrize("language", ["pt-BR", "en"])
def test_gemini_keeps_the_legacy_key_in_both_languages(tmp_path: Path, language: str) -> None:
    settings = make_settings(tmp_path)
    tts = gemini(
        voices=settings.gemini_tts.voices, styles=settings.gemini_tts.styles, model=settings.gemini_tts.model
    )
    assert tts.fingerprint(req(language=language)) == voice_fingerprint(settings, "gemini", language)


@pytest.mark.parametrize("language", ["pt-BR", "en"])
def test_kokoro_keeps_the_legacy_key_with_and_without_pauses(tmp_path: Path, language: str) -> None:
    settings = make_settings(tmp_path)
    tts = KokoroTTS(settings.kokoro.voices, pause_ms=settings.kokoro.pause_ms)
    legacy = voice_fingerprint(settings, "kokoro", language)
    assert tts.fingerprint(req(language=language)) == legacy
    assert tts.fingerprint(req(PAUSE, language)) == f"{legacy}|pausa{settings.kokoro.pause_ms}"


def cloned_settings(tmp_path: Path, provider: str) -> tuple[Settings, ChatterboxTTS]:
    settings = make_settings(tmp_path)
    reference = tmp_path / "ref.wav"
    reference.write_bytes(b"gravacao-de-referencia")
    chatterbox = settings.chatterbox.model_copy(update={"reference": reference})
    settings = settings.model_copy(update={"chatterbox": chatterbox})
    tts = make_chatterbox(
        None, tmp_path, provider=provider, pause_ms=chatterbox.pause_ms, model=chatterbox.model
    )
    tts._reference = reference  # a mesma gravação nos dois lados
    return settings, tts


@pytest.mark.parametrize("provider", ["chatterbox", "chatterbox_modal"])
def test_chatterbox_keeps_the_legacy_key_for_plain_pause_and_long_speech(
    tmp_path: Path, provider: str
) -> None:
    settings, tts = cloned_settings(tmp_path, provider)
    legacy = voice_fingerprint(settings, provider, "pt-BR")
    pause = f"|pausa{settings.chatterbox.pause_ms}"
    assert tts.fingerprint(req()) == legacy
    assert tts.fingerprint(req(PAUSE)) == legacy + pause
    assert long_speech_tag(provider, LONG) == f"|frases{ChatterboxConstants.MAX_PART_CHARS}"
    assert tts.fingerprint(req(LONG)) == legacy + long_speech_tag(provider, LONG)
    assert tts.fingerprint(req(PAUSE + " " + LONG)) == legacy + pause + long_speech_tag(provider, LONG)


def test_the_long_wav_name_does_not_change_for_the_same_input(tmp_path: Path) -> None:
    settings, tts = cloned_settings(tmp_path, "chatterbox_modal")
    legacy_fingerprint = voice_fingerprint(settings, "chatterbox_modal", "pt-BR")
    legacy_tags = f"|pausa400{long_speech_tag('chatterbox_modal', PAUSE)}"
    legacy_name = hashlib.sha256(f"{legacy_fingerprint}{legacy_tags}|{PAUSE}".encode()).hexdigest()[:10]
    assert long_digest(tts.fingerprint(req(PAUSE)), PAUSE) == legacy_name


def test_the_short_name_does_not_change_for_the_same_input(tmp_path: Path) -> None:
    """O Short nunca pôs pausa nem fala longa na chave: a identidade sem o texto reproduz o nome de hoje."""
    settings = make_settings(tmp_path)
    kokoro = KokoroTTS(settings.kokoro.voices, pause_ms=settings.kokoro.pause_ms)
    line = Line(scene="S01", text=PAUSE)
    legacy = wav_name(line, 0, "kokoro", voice_fingerprint(settings, "kokoro", "pt-BR"), "pt-BR")
    stem = legacy.rsplit("-", 1)[0]
    digest = long_digest(kokoro.fingerprint(req("", "pt-BR")), PAUSE)  # sem texto: sem `|pausa`
    assert legacy == f"{stem}-{digest}.wav"
    assert kokoro.fingerprint(req(PAUSE)) != kokoro.fingerprint(
        req("")
    )  # com texto, a pausa identifica a fala


# --- Parâmetros efetivos do Chatterbox ----------------------------------------------------------


def test_delivery_names_carry_the_values_and_unknown_falls_back_to_neutral_explicitly(tmp_path: Path) -> None:
    tts = make_chatterbox(None, tmp_path)
    neutral = tts.fingerprint(req())
    assert (
        tts.fingerprint(req(delivery="hook")) == f"{neutral}|entrega:hook=0.8,0.3"
    )  # declarado: antes sem valores
    assert tts.fingerprint(req(delivery="calm")) == f"{neutral}|entrega:calm=0.4,0.6"
    assert tts.fingerprint(req(delivery="gritado")) == neutral  # a síntese usa a neutra, a identidade também


def test_changing_a_delivery_parameter_invalidates_only_the_deliveries_it_affects(tmp_path: Path) -> None:
    base = make_chatterbox(None, tmp_path)
    hook = {
        "hook": {"exaggeration": 0.9, "cfg_weight": 0.3},
        "neutral": {"exaggeration": 0.5, "cfg_weight": 0.5},
    }
    changed = make_chatterbox(None, tmp_path, delivery={**ChatterboxConstants.DEFAULT_DELIVERY, **hook})
    assert changed.fingerprint(req(delivery="hook")) != base.fingerprint(req(delivery="hook"))
    assert changed.fingerprint(req()) == base.fingerprint(req())  # a neutra não mudou
    assert changed.fingerprint(req(delivery="calm")) == base.fingerprint(req(delivery="calm"))


def test_changing_the_neutral_parameters_invalidates_neutral_and_its_fallback_only(tmp_path: Path) -> None:
    base = make_chatterbox(None, tmp_path)
    delivery = {**ChatterboxConstants.DEFAULT_DELIVERY, "neutral": {"exaggeration": 0.6, "cfg_weight": 0.5}}
    changed = make_chatterbox(None, tmp_path, delivery=delivery)
    assert changed.fingerprint(req()) == f"{base.fingerprint(req())}|neutro=0.6,0.5"
    assert changed.fingerprint(req(delivery="gritado")) == changed.fingerprint(
        req()
    )  # o fallback segue a neutra
    assert changed.fingerprint(req(delivery="hook")) == base.fingerprint(
        req(delivery="hook")
    )  # a hook não usa a neutra


def test_the_reference_the_pause_and_the_algorithm_version_are_part_of_the_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tts = make_chatterbox(None, tmp_path)
    before = tts.fingerprint(req())
    (tmp_path / "voz.wav").write_bytes(b"outra gravacao")
    assert reference_hash(tmp_path / "voz.wav") in tts.fingerprint(req()) and tts.fingerprint(req()) != before
    assert make_chatterbox(None, tmp_path, pause_ms=700).fingerprint(req(PAUSE)) != tts.fingerprint(
        req(PAUSE)
    )
    assert make_chatterbox(None, tmp_path, pause_ms=700).fingerprint(req()) == tts.fingerprint(
        req()
    )  # sem pausa
    monkeypatch.setattr(ChatterboxConstants, "SPEECH_VERSION", 2)
    assert tts.fingerprint(req()).endswith("|v2")  # mudar o corte e a junção regenera as falas afetadas


# --- A identidade e a síntese recusam o mesmo pedido --------------------------------------------


def test_fingerprint_refuses_what_synthesis_would_refuse(tmp_path: Path) -> None:
    tts = make_chatterbox(None, tmp_path)
    with pytest.raises(ModelUnavailable, match="idioma"):
        tts.fingerprint(req(language="xx"))
    with pytest.raises(ModelUnavailable, match="idioma"):
        tts.synthesize_speech(req(language="xx"))
    (tmp_path / "voz.wav").unlink()
    with pytest.raises(ModelUnavailable, match="referência"):
        tts.fingerprint(req())
    with pytest.raises(ProviderError, match="glossário"):
        gemini().fingerprint(replace(req(), lexicon={"FBI": "efe bê i"}))
    with pytest.raises(ModelUnavailable, match="sem voz"):
        gemini().fingerprint(req(language="es"))


def test_kokoro_lexicon_is_part_of_the_identity_and_the_voice_override_too() -> None:
    tts = KokoroTTS({"pt-BR": "pm_alex"}, pause_ms=300)
    plain = tts.fingerprint(req())
    assert tts.fingerprint(replace(req(), lexicon={"FBI": "efebêi"})) != plain
    assert tts.fingerprint(req(voice="pm_santa")) == "kokoro|pm_santa"
