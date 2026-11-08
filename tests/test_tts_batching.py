"""RF3: lote, fallback por cena, cota, WAV inválido e fechamento do TTS, provados com `FakeBatchTTS`."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from app.media.speech_batches import group_requests, synthesize_requests
from app.pipeline.schemas import Status
from app.providers.errors import InvalidOutput, ModelUnavailable, ProviderError, QuotaExhausted
from app.providers.tts.base import Closeable, SpeechRequest, SpeechResult, closing_tts
from tests.fakes import FakeBatchTTS, FakeTTS


def requests(
    tmp_path: Path, *texts: str, language: str = "pt-BR", voice: str | None = None
) -> list[SpeechRequest]:
    return [
        SpeechRequest(
            text=text, out_path=tmp_path / "voice" / f"S{i:02d}.wav", language=language, voice=voice
        )
        for i, text in enumerate(texts, 1)
    ]


def names(groups: list[list[SpeechRequest]]) -> list[list[str]]:
    return [[r.out_path.stem for r in group] for group in groups]


# --- Agrupamento --------------------------------------------------------------------------------


def test_grouping_respects_the_limit_the_voice_the_language_and_the_pauses(tmp_path: Path) -> None:
    plain = requests(tmp_path, "a" * 40, "b" * 40, "c" * 40, "d" * 40)
    assert names(group_requests(plain, 100)) == [["S01", "S02"], ["S03", "S04"]]  # limite de caracteres
    english = replace(plain[1], language="en")
    assert names(group_requests([plain[0], english], 999)) == [
        ["S01"],
        ["S02"],
    ]  # idioma diferente: outra chamada
    mixed = [*requests(tmp_path, "um", voice="A"), *requests(tmp_path, "dois", voice="B")]
    assert len(group_requests(mixed, 999)) == 2  # voz diferente também não
    pauses = requests(tmp_path, "antes", "meio <short pause> meio", "depois")
    assert names(group_requests(pauses, 999)) == [["S01"], ["S02"], ["S03"]]  # pausa vai sozinha (ADR 015)
    glossary = [SpeechRequest(text="x", out_path=tmp_path / "g.wav", lexicon={"FBI": "efe"})]
    assert len(group_requests([*requests(tmp_path, "oi"), *glossary], 999)) == 2


@pytest.mark.parametrize("limit", [1, 30, 80, 1200])
def test_grouping_keeps_order_and_cardinality(tmp_path: Path, limit: int) -> None:
    reqs = requests(tmp_path, *("palavra " * n for n in (3, 9, 1, 12, 5, 2, 20)))
    groups = group_requests(reqs, limit)
    assert [r for group in groups for r in group] == reqs
    assert all(len(g) == 1 or sum(len(r.text) for r in g) <= limit for g in groups)  # só a maior vai sozinha


# --- Chamadas -----------------------------------------------------------------------------------


def test_a_batching_provider_gets_one_call_per_group_and_every_outcome_in_order(tmp_path: Path) -> None:
    tts = FakeBatchTTS(max_batch_chars=45)
    reqs = requests(tmp_path, "um dois três", "quatro cinco seis", "sete oito nove", "dez onze doze")
    outcomes = synthesize_requests(tts, reqs)
    assert tts.calls == [
        ["S01.wav", "S02.wav", "S03.wav"],
        ["S04.wav"],
    ]  # 12+17+14 = 43 cabem em 45; com a 4ª (13), não
    assert [o.scene_id for o in outcomes] == [r.out_path.name for r in reqs]
    assert all(
        o.status is Status.COMPLETED and o.value == r.out_path for o, r in zip(outcomes, reqs, strict=True)
    )
    assert all(r.out_path.is_file() for r in reqs)


def test_a_provider_without_batches_gets_one_call_per_request(tmp_path: Path) -> None:
    calls: list[str] = []

    class Plain(FakeTTS):
        def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
            calls.append(request.out_path.name)
            return super().synthesize_speech(request)

    outcomes = synthesize_requests(Plain(), requests(tmp_path, "a", "b", "c"))
    assert calls == ["S01.wav", "S02.wav", "S03.wav"] and all(o.status is Status.COMPLETED for o in outcomes)


def test_only_the_expected_cut_refusal_falls_back_to_scene_by_scene(tmp_path: Path) -> None:
    tts = FakeBatchTTS(batch_error=InvalidOutput("fake", "corte duvidoso"))
    outcomes = synthesize_requests(tts, requests(tmp_path, "a", "b", "c"))
    assert tts.calls == [["S01.wav", "S02.wav", "S03.wav"], ["S01.wav"], ["S02.wav"], ["S03.wav"]]
    assert [o.status for o in outcomes] == [Status.COMPLETED] * 3


def test_another_batch_error_is_not_retried_scene_by_scene(tmp_path: Path) -> None:
    tts = FakeBatchTTS(batch_error=ProviderError("fake", "serviço fora do ar"))
    outcomes = synthesize_requests(tts, requests(tmp_path, "a", "b"))
    assert tts.calls == [["S01.wav", "S02.wav"]]  # nenhuma rajada de chamadas individuais
    assert [(o.status, o.reason) for o in outcomes] == [(Status.NEEDS_REVIEW, "provider_error")] * 2
    assert not any((tmp_path / "voice").glob("*.wav"))


def test_exhausted_quota_stops_every_further_call(tmp_path: Path) -> None:
    tts = FakeBatchTTS(max_batch_chars=13, batch_error=QuotaExhausted("fake", "10 por dia"))
    outcomes = synthesize_requests(tts, requests(tmp_path, "aaaaaa", "bbbbbb", "cccccc", "dddddd"))
    assert tts.calls == [["S01.wav", "S02.wav"]]  # o segundo grupo nem foi tentado
    assert {o.reason for o in outcomes} == {"quota_exhausted"} and len(outcomes) == 4
    assert "não tentada" in outcomes[-1].detail


def test_quota_in_one_scene_skips_the_rest_but_keeps_what_was_generated(tmp_path: Path) -> None:
    tts = FakeTTS()
    real = tts.synthesize_speech

    def flaky(request: SpeechRequest) -> SpeechResult:
        if request.out_path.name == "S02.wav":
            raise QuotaExhausted("fake", "cota")
        return real(request)

    tts.synthesize_speech = flaky  # type: ignore[method-assign]
    outcomes = synthesize_requests(tts, requests(tmp_path, "a", "b", "c"))
    assert [(o.status, o.reason) for o in outcomes] == [
        (Status.COMPLETED, ""),
        (Status.NEEDS_REVIEW, "quota_exhausted"),
        (Status.NEEDS_REVIEW, "quota_exhausted"),
    ]
    assert (tmp_path / "voice" / "S01.wav").is_file() and not (tmp_path / "voice" / "S03.wav").exists()


def test_a_failed_scene_leaves_the_others_and_a_scene_error_is_its_own(tmp_path: Path) -> None:
    tts = FakeBatchTTS(scene_errors={"S02.wav": ModelUnavailable("fake", "sem voz")})
    outcomes = synthesize_requests(tts, requests(tmp_path, "a", "b", "c"))
    # o lote falha (ModelUnavailable) e vale para o grupo; fora de lote a cena falha sozinha
    assert tts.calls == [["S01.wav", "S02.wav", "S03.wav"]]
    assert {o.reason for o in outcomes} == {"model_unavailable"}
    single = synthesize_requests(
        FakeBatchTTS(max_batch_chars=1, scene_errors={"S02.wav": ModelUnavailable("fake", "sem voz")}),
        requests(tmp_path, "a", "b", "c"),
    )
    assert [o.status for o in single] == [Status.COMPLETED, Status.NEEDS_REVIEW, Status.COMPLETED]


def test_programming_errors_are_not_swallowed(tmp_path: Path) -> None:
    with pytest.raises(KeyError):
        synthesize_requests(FakeBatchTTS(batch_error=KeyError("bug")), requests(tmp_path, "a", "b"))


# --- Arquivos -----------------------------------------------------------------------------------


def test_an_invalid_wav_is_not_a_success_and_is_removed(tmp_path: Path) -> None:
    class Junk(FakeTTS):
        def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
            request.out_path.parent.mkdir(parents=True, exist_ok=True)
            request.out_path.write_bytes(b"isto nao e um wav")
            return SpeechResult(path=request.out_path, model="m", voice="v")

    reqs = requests(tmp_path, "a")
    [outcome] = synthesize_requests(Junk(), reqs)
    assert (outcome.status, outcome.reason) == (Status.NEEDS_REVIEW, "invalid_output")
    assert not reqs[0].out_path.exists()


def test_a_previous_wav_survives_a_failed_run(tmp_path: Path) -> None:
    reqs = requests(tmp_path, "a")
    reqs[0].out_path.parent.mkdir(parents=True)
    reqs[0].out_path.write_bytes(b"RIFF....WAVE" + b"\x00" * 64)
    tts = FakeBatchTTS(scene_errors={"S01.wav": ProviderError("fake", "falhou")})
    [outcome] = synthesize_requests(tts, reqs)
    assert outcome.status is Status.NEEDS_REVIEW and reqs[0].out_path.read_bytes().startswith(b"RIFF")


def test_a_batch_that_returns_the_wrong_files_is_a_group_failure(tmp_path: Path) -> None:
    class Wrong(FakeBatchTTS):
        def synthesize_many(self, requests: list[SpeechRequest]) -> list[SpeechResult]:  # type: ignore[override]
            return [SpeechResult(path=tmp_path / "outro.wav", model="m", voice="v")]

    outcomes = synthesize_requests(Wrong(), requests(tmp_path, "a", "b"))
    assert {o.status for o in outcomes} == {Status.NEEDS_REVIEW}


# --- Ciclo de vida ------------------------------------------------------------------------------


def test_closing_tts_closes_on_success_and_on_error_and_skips_what_cannot_close() -> None:
    tts = FakeBatchTTS()
    assert isinstance(tts, Closeable) and not isinstance(FakeTTS(), Closeable)
    with closing_tts(tts):
        pass
    with pytest.raises(RuntimeError), closing_tts(tts):
        raise RuntimeError("falhou no meio")
    assert tts.closed == 2
    with closing_tts(FakeTTS()):  # sem close(): nada a fechar, sem erro
        pass
