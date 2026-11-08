"""RF6 (voz): os nomes de WAV de hoje não mudam, e uma fala nova só substitui a antiga quando fica pronta."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.media.probe import ProbeError
from app.pipeline.models.naming import Naming
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.models.status import Status
from app.pipeline.models.voice_key import VoiceKey
from app.pipeline.voice import Narrator, VoiceLibrary
from app.providers.errors import QuotaExhausted
from app.providers.tts.kokoro import KokoroTTS
from tests.fakes import FakeBatchTTS, FakeTTS, make_settings, wav_duration_ms
from tests.legacy_voice_names import long_name, short_name, voice_fingerprint
from tests.test_tts_fingerprint import LONG, PAUSE, PLAIN, cloned_settings, gemini


def seconds(path: Path) -> float:
    return wav_duration_ms(path) / 1000


def narrator(tts, folder: Path, naming: Naming = Naming.LONG, **kw) -> Narrator:  # type: ignore[no-untyped-def]
    return Narrator(tts, "pt-BR", VoiceLibrary(folder, naming), kw.pop("measure", seconds), **kw)


# --- Os nomes de hoje -------------------------------------------------------------------------------------

TEXTS = [PLAIN, PAUSE, LONG, f"{PAUSE} {LONG}"]
DELIVERIES = ["neutral", "hook", "calm"]


def adapters(tmp_path: Path) -> dict[str, tuple]:  # type: ignore[type-arg]
    settings = make_settings(tmp_path)
    gm = settings.gemini_tts
    found = {
        "kokoro": (KokoroTTS(settings.kokoro.voices, pause_ms=settings.kokoro.pause_ms), settings),
        "gemini": (gemini(model=gm.model, voices=gm.voices, styles=gm.styles), settings),
    }
    for provider in ("chatterbox", "chatterbox_modal"):
        configured, tts = cloned_settings(tmp_path, provider)
        found[provider] = (tts, configured)
    return found


@pytest.mark.parametrize("provider", ["kokoro", "gemini", "chatterbox", "chatterbox_modal"])
@pytest.mark.parametrize("text", TEXTS)
def test_the_short_name_is_the_one_made_before(tmp_path: Path, provider: str, text: str) -> None:
    """Decisão do dono: os WAVs dos Shorts aprovados na escuta não são regerados, nem com pausa ou entrega."""
    tts, settings = adapters(tmp_path)[provider]
    legacy = voice_fingerprint(settings, provider, "pt-BR")
    for index, delivery in enumerate(DELIVERIES):
        stem = f"fora-{index}" if index == 1 else f"S0{index}"
        expected = short_name(stem, provider, legacy, delivery, text)
        key = narrator(tts, tmp_path, Naming.SHORT).key(SpeechLine(stem, text, delivery))
        assert key.file_name(Naming.SHORT) == expected, f"{provider} / {delivery}"


@pytest.mark.parametrize("provider", ["kokoro", "gemini", "chatterbox", "chatterbox_modal"])
@pytest.mark.parametrize("text", TEXTS)
def test_the_long_name_is_the_one_made_before(tmp_path: Path, provider: str, text: str) -> None:
    tts, settings = adapters(tmp_path)[provider]
    for delivery in [*DELIVERIES, "turn", "invite"]:  # as vozes clonadas levam a entrega no nome
        expected = long_name(settings, provider, "S01", text, delivery, "pt-BR")
        key = narrator(tts, tmp_path).key(SpeechLine("S01", text, delivery))
        assert key.file_name(Naming.LONG) == expected, f"{provider} / {delivery}"


def test_the_name_uses_the_cache_identity_not_the_display_name(tmp_path: Path) -> None:
    key = narrator(gemini(), tmp_path).key(SpeechLine("S01", PLAIN))
    assert key.provider == "gemini" and key.file_name(Naming.LONG).startswith(
        "S01-gemini-"
    )  # não `gemini_tts`


def test_a_changed_glossary_or_text_changes_the_name_and_nothing_else_does(tmp_path: Path) -> None:
    tts = FakeBatchTTS()
    plain = narrator(tts, tmp_path).key(SpeechLine("S01", "Um objeto JSON."))
    spelled = narrator(tts, tmp_path, respell=lambda t: t.replace("JSON", "jêison")).key(
        SpeechLine("S01", "Um objeto JSON.")
    )
    assert spelled.spoken == "Um objeto jêison." and spelled.digest != plain.digest
    assert (
        narrator(tts, tmp_path).key(SpeechLine("S01", "Um objeto JSON.")) == plain
    )  # a mesma entrada, a mesma chave
    assert (
        narrator(tts, tmp_path).key(SpeechLine("S02", "Um objeto JSON.")).digest == plain.digest
    )  # a cena fica no stem


def test_the_stem_separates_scene_provider_and_language() -> None:
    key = VoiceKey("fora-1", "chatterbox_modal", "pt-BR", "fp", "texto")
    assert key.stem(Naming.LONG) == "fora-1-chatterbox_modal"
    assert key.stem(Naming.SHORT) == "fora-1-chatterbox_modal-ptbr"
    assert key.file_name(Naming.SHORT) == f"fora-1-chatterbox_modal-ptbr-{key.digest}.wav"


# --- A biblioteca -------------------------------------------------------------------------------------------


def test_the_library_finds_only_the_older_versions_of_the_same_speech(tmp_path: Path) -> None:
    library = VoiceLibrary(tmp_path, Naming.SHORT)
    key = VoiceKey("S01", "kokoro", "pt-BR", "fp", "texto novo")
    names = [
        f"S01-kokoro-ptbr-{'a' * 10}.wav",  # a mesma fala, outro hash: velha
        f"S01-kokoro-en-{'b' * 10}.wav",  # outro idioma
        f"S01-gemini-ptbr-{'c' * 10}.wav",  # outro provedor
        f"S10-kokoro-ptbr-{'d' * 10}.wav",  # outra cena
        "S01-kokoro-ptbr-curto.wav",  # não é um hash
        key.file_name(Naming.SHORT),  # a atual
    ]
    for name in names:
        (tmp_path / name).write_bytes(b"x")
    assert [p.name for p in library.stale(key)] == [names[0]]
    assert library.prune(key) == [tmp_path / names[0]]
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(names[1:])


# --- O narrador ---------------------------------------------------------------------------------------------

LINES = [
    SpeechLine("S01", "Primeira fala."),
    SpeechLine("S02", "Segunda fala."),
    SpeechLine("S03", "Terceira."),
]


def test_only_the_missing_speeches_are_planned_and_generated_in_one_batch(tmp_path: Path) -> None:
    tts = FakeBatchTTS()
    first = narrator(tts, tmp_path).produce(LINES)
    assert [(o.scene_id, o.status) for o in first] == [(line.id, Status.COMPLETED) for line in LINES]
    assert tts.calls == [[o.value.name for o in first]]  # uma chamada em lote para as três
    again = FakeBatchTTS()
    assert narrator(again, tmp_path).plan(LINES) == [] and again.calls == []  # nada falta
    assert [o.value for o in narrator(again, tmp_path).produce(LINES)] == [o.value for o in first]


def test_a_failed_speech_keeps_the_others_and_a_new_process_asks_only_for_it(tmp_path: Path) -> None:
    probe = narrator(FakeTTS(), tmp_path)
    failing_name = probe.key(LINES[1]).file_name(Naming.LONG)
    tts = FakeBatchTTS(max_batch_chars=1, scene_errors={failing_name: QuotaExhausted("fake", "cota")})
    outcomes = narrator(tts, tmp_path).produce(LINES)
    assert [(o.scene_id, o.status, o.reason) for o in outcomes] == [
        ("S01", Status.COMPLETED, ""),
        ("S02", Status.NEEDS_REVIEW, "quota_exhausted"),
        ("S03", Status.NEEDS_REVIEW, "quota_exhausted"),  # a cota esgotada para as chamadas seguintes
    ]
    retry = FakeBatchTTS()
    narrator(retry, tmp_path).produce(LINES)  # outro processo: o cache são os nomes dos arquivos
    assert sorted(n for call in retry.calls for n in call) == sorted(
        [probe.key(LINES[1]).file_name(Naming.LONG), probe.key(LINES[2]).file_name(Naming.LONG)]
    )


def test_a_new_version_replaces_the_old_one_only_after_it_is_ready(tmp_path: Path) -> None:
    tts = FakeBatchTTS()
    old = narrator(tts, tmp_path).produce([SpeechLine("S01", "Texto antigo.")])[0].value
    changed = SpeechLine("S01", "Texto novo.")
    new_name = narrator(tts, tmp_path).key(changed).file_name(Naming.LONG)
    failing = FakeBatchTTS(scene_errors={new_name: QuotaExhausted("fake", "cota")})
    [outcome] = narrator(failing, tmp_path).produce([changed])
    assert outcome.status is Status.NEEDS_REVIEW and old.is_file() and not (tmp_path / new_name).exists()
    [done] = narrator(tts, tmp_path).produce([changed])  # agora a nova fica pronta e a antiga sai
    assert done.status is Status.COMPLETED and done.value.name == new_name
    assert not old.exists() and sorted(p.name for p in tmp_path.iterdir()) == [new_name]


def test_a_wav_that_does_not_measure_is_not_a_success_and_keeps_the_old_one(tmp_path: Path) -> None:
    tts = FakeBatchTTS()
    old = narrator(tts, tmp_path).produce([SpeechLine("S01", "Texto antigo.")])[0].value
    [bad] = narrator(tts, tmp_path, measure=lambda p: 0.0).produce([SpeechLine("S01", "Texto novo.")])
    assert (bad.status, bad.reason) == (Status.NEEDS_REVIEW, "invalid_output")
    assert old.is_file() and [p.name for p in tmp_path.iterdir()] == [old.name]  # nem a nova sobra
    [unreadable] = narrator(tts, tmp_path, measure=_raises).produce([SpeechLine("S01", "Outro.")])
    assert unreadable.status is Status.NEEDS_REVIEW and [p.name for p in tmp_path.iterdir()] == [old.name]


def _raises(path: Path) -> float:
    raise ProbeError("ffprobe não leu")


def test_a_corrupt_wav_in_the_place_of_a_speech_is_generated_again(tmp_path: Path) -> None:
    tts = FakeBatchTTS()
    path = narrator(tts, tmp_path).produce([SpeechLine("S01", "Fala.")])[0].value
    path.write_bytes(b"corrompido")
    assert len(narrator(FakeBatchTTS(), tmp_path).plan([SpeechLine("S01", "Fala.")])) == 1
    [outcome] = narrator(tts, tmp_path).produce([SpeechLine("S01", "Fala.")])
    assert outcome.status is Status.COMPLETED and wav_duration_ms(path) > 0


def test_lines_without_a_scene_keep_their_own_stem_in_the_short(tmp_path: Path) -> None:
    tts = FakeTTS()
    outcomes = narrator(tts, tmp_path, Naming.SHORT).produce(
        [SpeechLine("fora-1", "Fala solta."), SpeechLine("S01", "Cena.")]
    )
    assert [o.scene_id for o in outcomes] == ["fora-1", "S01"]
    assert outcomes[0].value.name.startswith("fora-1-fake-ptbr-")
