"""Adapter Chatterbox (ADR 016) com um processo de modelo falso: sem rede, sem o modelo e sem voz real."""

from __future__ import annotations

import importlib.util
import tempfile
import wave
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from app.bootstrap import build_context
from app.providers.base import ProviderInfo
from app.providers.errors import ModelUnavailable, ProviderError
from app.providers.tts.base import SpeechRequest
from app.providers.tts.chatterbox import ChatterboxTTS, reference_hash
from app.settings import CONFIG_FILE, load_settings, speech_chars_per_second

REPO_ROOT = Path(__file__).resolve().parents[1]
SP = "<short pause>"


def write_wav(path: Path, frames: int = 2400) -> None:
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(b"\x00\x00" * frames)


class FakeWorker:
    """Faz o papel do processo do modelo: guarda os pedidos e grava um WAV mudo."""

    def __init__(self, answer: Mapping[str, Any] | None = None, error: Exception | None = None) -> None:
        self.jobs: list[Mapping[str, Any]] = []
        self.answer = answer
        self.error = error
        self.closed = False

    def ask(self, job: Mapping[str, Any]) -> dict[str, Any]:
        self.jobs.append(job)
        if self.error:
            raise self.error
        if self.answer is not None:
            return dict(self.answer)
        write_wav(Path(job["out_path"]))
        return {"ok": True, "seconds": 0.1}

    def close(self) -> None:
        self.closed = True


def make_tts(worker: FakeWorker | None = None, folder: Path | None = None, **kwargs: Any) -> ChatterboxTTS:
    folder = folder or Path(tempfile.mkdtemp())
    python, reference = folder / "python", folder / "voz.wav"
    python.write_text("")
    write_wav(reference)
    fake = worker or FakeWorker()
    starts: list[tuple[Path, str, int]] = []

    def start(python: Path, model: str, threads: int) -> FakeWorker:
        starts.append((python, model, threads))
        return fake

    tts = ChatterboxTTS(
        python, reference, language_ids={"en": "en", "pt-BR": "pt"}, start=start,
        **{"num_threads": 4, "pause_ms": 400, **kwargs},
    )
    tts.starts = starts  # type: ignore[attr-defined]
    return tts


def test_is_local_and_free() -> None:
    assert make_tts().info == ProviderInfo("chatterbox", remote=False, usd_per_call=0)


def test_one_scene_is_one_job_with_the_reference_voice(tmp_path: Path) -> None:
    worker = FakeWorker()
    tts = make_tts(worker, tmp_path)
    out = tmp_path / "voice" / "S01.wav"
    result = tts.synthesize_speech(SpeechRequest(text="Uma fala só.", out_path=out, language="pt-BR"))
    assert worker.jobs == [{
        "parts": ["Uma fala só."], "language_id": "pt", "reference": str(tmp_path / "voz.wav"),
        "out_path": str(out), "pause_ms": 400,
        "exaggeration": 0.5,
        "cfg_weight": 0.5,
    }]
    assert result.path == out and out.is_file()
    assert result.model == "chatterbox-multilingual-v3"
    assert result.voice == f"clone:{reference_hash(tmp_path / 'voz.wav')}"


def test_delivery_sets_the_expressiveness_and_unknown_falls_back_to_neutral(tmp_path: Path) -> None:
    worker = FakeWorker()
    tts = make_tts(worker, tmp_path)
    for delivery in ("neutral", "hook", "calm", "gritado"):
        out = tmp_path / f"{delivery}.wav"
        tts.synthesize_speech(SpeechRequest(text="Oi.", out_path=out, language="pt-BR", delivery=delivery))
    params = [(j["exaggeration"], j["cfg_weight"]) for j in worker.jobs]
    assert params == [(0.5, 0.5), (0.8, 0.3), (0.4, 0.6), (0.5, 0.5)]


def test_delivery_values_come_from_the_config(tmp_path: Path) -> None:
    worker = FakeWorker()
    tts = make_tts(worker, tmp_path, delivery={"neutral": {"exaggeration": 0.4, "cfg_weight": 0.6},
                                               "hook": {"exaggeration": 1.0, "cfg_weight": 0.2}})
    request = SpeechRequest(text="Oi.", out_path=tmp_path / "h.wav", language="pt-BR", delivery="hook")
    tts.synthesize_speech(request)
    assert (worker.jobs[0]["exaggeration"], worker.jobs[0]["cfg_weight"]) == (1.0, 0.2)
    settings = load_settings(REPO_ROOT)
    assert settings.chatterbox.delivery["hook"].exaggeration == 0.8
    assert settings.chatterbox.delivery["neutral"].cfg_weight == 0.5
    assert list(settings.chatterbox.delivery) == ["hook", "turn", "invite", "neutral", "calm"]


def test_pauses_split_the_text_and_the_tag_never_reaches_the_model(tmp_path: Path) -> None:
    worker = FakeWorker()
    text = f"Quanto vale? {SP} Perto de trinta milhões."
    make_tts(worker, tmp_path).synthesize_speech(
        SpeechRequest(text=text, out_path=tmp_path / "S01.wav", language="pt-BR")
    )
    assert worker.jobs[0]["parts"] == ["Quanto vale?", "Perto de trinta milhões."]
    assert worker.jobs[0]["pause_ms"] == 400


def test_the_model_loads_once_for_many_scenes(tmp_path: Path) -> None:
    tts = make_tts(folder=tmp_path)
    for scene in ("S01", "S02", "S03"):
        out = tmp_path / f"{scene}.wav"
        tts.synthesize_speech(SpeechRequest(text="Fala.", out_path=out, language="pt-BR"))
    assert tts.starts == [(tmp_path / "python", "v3", 4)]  # type: ignore[attr-defined]


def test_missing_environment_or_reference_is_model_unavailable(tmp_path: Path) -> None:
    request = SpeechRequest(text="Fala.", out_path=tmp_path / "S01.wav", language="pt-BR")
    ids = {"pt-BR": "pt"}
    with pytest.raises(ModelUnavailable, match="CHATTERBOX_PYTHON"):
        ChatterboxTTS(None, None, language_ids=ids).synthesize_speech(request)
    python = tmp_path / "python"
    python.write_text("")
    with pytest.raises(ModelUnavailable, match="CHATTERBOX_REFERENCE"):
        ChatterboxTTS(python, tmp_path / "nao-existe.wav", language_ids=ids).synthesize_speech(request)


def test_language_without_a_model_code_is_model_unavailable(tmp_path: Path) -> None:
    with pytest.raises(ModelUnavailable, match="idioma"):
        make_tts(folder=tmp_path).synthesize_speech(
            SpeechRequest(text="Rede.", out_path=tmp_path / "S01.wav", language="de")
        )


def test_model_that_does_not_load_is_model_unavailable(tmp_path: Path) -> None:
    python, reference = tmp_path / "python", tmp_path / "voz.wav"
    python.write_text("")
    write_wav(reference)

    def start(python: Path, model: str, threads: int) -> FakeWorker:
        raise RuntimeError("o processo do modelo terminou (código 1)")

    tts = ChatterboxTTS(python, reference, language_ids={"pt-BR": "pt"}, start=start)
    with pytest.raises(ModelUnavailable, match="não carregou"):
        tts.synthesize_speech(SpeechRequest(text="Fala.", out_path=tmp_path / "S01.wav", language="pt-BR"))


def test_worker_error_is_a_provider_error_and_the_process_restarts(tmp_path: Path) -> None:
    request = SpeechRequest(text="Fala.", out_path=tmp_path / "S01.wav", language="pt-BR")
    refused = make_tts(FakeWorker(answer={"ok": False, "error": "RuntimeError: sem memória"}), tmp_path)
    with pytest.raises(ProviderError, match="sem memória"):
        refused.synthesize_speech(request)
    broken = make_tts(FakeWorker(error=RuntimeError("o processo do modelo terminou (código -9)")), tmp_path)
    with pytest.raises(ProviderError, match="falhou"):
        broken.synthesize_speech(request)
    with pytest.raises(ProviderError):
        broken.synthesize_speech(request)
    assert len(broken.starts) == 2  # type: ignore[attr-defined]  # subiu de novo depois da falha


def test_answer_without_a_file_is_a_provider_error(tmp_path: Path) -> None:
    tts = make_tts(FakeWorker(answer={"ok": True, "seconds": 1.0}), tmp_path)
    with pytest.raises(ProviderError, match="nenhum áudio"):
        tts.synthesize_speech(SpeechRequest(text="Fala.", out_path=tmp_path / "S01.wav", language="pt-BR"))


def test_close_stops_the_model_process(tmp_path: Path) -> None:
    worker = FakeWorker()
    tts = make_tts(worker, tmp_path)
    tts.synthesize_speech(SpeechRequest(text="Fala.", out_path=tmp_path / "S01.wav", language="pt-BR"))
    tts.close()
    assert worker.closed


def test_paths_come_from_the_environment_and_drafts_stay_on_kokoro(tmp_path: Path) -> None:
    env = {"CHATTERBOX_PYTHON": "/opt/voz/bin/python", "CHATTERBOX_REFERENCE": "~/voz/referencia.wav"}
    settings = load_settings(REPO_ROOT, env)
    assert settings.chatterbox.python == Path("/opt/voz/bin/python")
    assert settings.chatterbox.reference == Path("~/voz/referencia.wav")
    # ADR 016: a voz clonada é a do vídeo final; os rascunhos seguem no Kokoro, que é rápido
    assert (settings.providers.tts, settings.providers.tts_final) == ("kokoro", "chatterbox_modal")  # ADR 024
    (tmp_path / CONFIG_FILE.parent).mkdir()  # sem `.env` ao lado, para não depender do desta máquina
    (tmp_path / CONFIG_FILE).write_text((REPO_ROOT / CONFIG_FILE).read_text())
    assert load_settings(tmp_path, {}).chatterbox.python is None


def test_voice_by_name_outside_the_config_choice() -> None:
    context = build_context(REPO_ROOT, {})
    assert context.tts_named("chatterbox").info.name == "chatterbox"
    with pytest.raises(Exception, match="não existe"):
        context.tts_named("vozinha")


def test_check_estimates_with_the_cloned_voice_rate() -> None:
    settings = load_settings(REPO_ROOT, {})
    assert speech_chars_per_second(settings) == settings.chatterbox.chars_per_second


def montar_module() -> Any:
    path = REPO_ROOT / "scripts" / "provisorio" / "montar_episodio.py"
    spec = importlib.util.spec_from_file_location("montar_episodio", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_reference_recording_is_part_of_the_voice_cache_key(tmp_path: Path) -> None:
    montar = montar_module()
    first, second = tmp_path / "a.wav", tmp_path / "b.wav"
    write_wav(first, 100)
    write_wav(second, 200)
    key = lambda ref: montar.voice_fingerprint(  # noqa: E731
        load_settings(REPO_ROOT, {"CHATTERBOX_REFERENCE": str(ref)}), "chatterbox", "pt-BR"
    )
    assert key(first) != key(second)
    assert key(first) == f"chatterbox|v3|pt|{reference_hash(first)}"


@pytest.mark.slow
def test_real_model_writes_a_wav(tmp_path: Path) -> None:
    """Modelo real, em CPU: minutos. Só roda com `pytest -m slow` e o ambiente do Chatterbox configurado."""
    settings = load_settings(REPO_ROOT)
    box = settings.chatterbox
    if not (box.python and box.reference):
        pytest.skip("CHATTERBOX_PYTHON e CHATTERBOX_REFERENCE ausentes")
    tts = ChatterboxTTS(
        box.python.expanduser(), box.reference.expanduser(), model=box.model, language_ids=box.language_ids,
        num_threads=box.num_threads, pause_ms=box.pause_ms,
    )
    out = tmp_path / "S01.wav"
    try:
        tts.synthesize_speech(SpeechRequest(text="Uma fala curta.", out_path=out, language="pt-BR"))
    finally:
        tts.close()
    with wave.open(str(out), "rb") as wav:
        assert wav.getnframes() > 0


# --- Fala longa: o modelo para em ~40 s por chamada (max_new_tokens=1000) ---------------------------------

FRASE = "Esta é a frase número {n}, que fala de um corte antigo entre o que depende e o que não."
LONG = " ".join(FRASE.format(n=n) for n in range(12))


def test_split_long_keeps_every_word_in_order_and_respects_the_limit() -> None:
    from app.providers.tts.chatterbox import MAX_PART_CHARS, split_long

    groups = split_long(LONG)
    assert len(groups) > 1
    assert all(len(group) <= MAX_PART_CHARS for group in groups)
    assert " ".join(groups).split() == LONG.split()
    assert all(group.endswith(".") for group in groups)  # corta no fim da frase


def test_split_long_breaks_a_huge_sentence_at_commas_then_words() -> None:
    from app.providers.tts.chatterbox import split_long

    sentence = ", ".join(f"item {n} da lista" for n in range(60)) + "."
    groups = split_long(sentence, limit=80)
    assert all(len(group) <= 80 for group in groups)
    assert " ".join(groups).split() == sentence.split()
    assert split_long("Curta.") == ["Curta."]
    assert split_long('Ele disse “basta.” Depois saiu.', limit=20) == ["Ele disse “basta.”", "Depois saiu."]


def test_short_scene_is_still_one_job_and_long_scene_is_joined_with_the_pauses(tmp_path: Path) -> None:
    from app.providers.tts.chatterbox import SENTENCE_GAP_MS

    worker = FakeWorker()
    tts = make_tts(worker, tmp_path)
    out = tmp_path / "voice" / "S02.wav"
    text = f"{LONG} {SP} Fim curto."
    tts.synthesize_speech(SpeechRequest(text=text, out_path=out, language="pt-BR"))
    assert len(worker.jobs) == 2  # um pedido por trecho entre pausas
    first, second = worker.jobs
    assert len(first["parts"]) > 1 and first["pause_ms"] == SENTENCE_GAP_MS
    assert second["parts"] == ["Fim curto."]
    assert " ".join(first["parts"]).split() == LONG.split()
    assert first["out_path"] != str(out) and not Path(first["out_path"]).exists()  # trechos temporários
    with wave.open(str(out), "rb") as wav:  # dois WAVs de 2400 quadros + 400 ms de pausa a 24 kHz
        assert wav.getnframes() == 2400 * 2 + 9600
    assert sorted(p.name for p in out.parent.iterdir()) == ["S02.wav"]


def test_a_failure_in_one_part_of_a_long_scene_is_a_provider_error(tmp_path: Path) -> None:
    worker = FakeWorker(answer={"ok": False, "error": "CUDA out of memory"})
    with pytest.raises(ProviderError, match="CUDA"):
        make_tts(worker, tmp_path).synthesize_speech(
            SpeechRequest(text=LONG, out_path=tmp_path / "S01.wav", language="pt-BR")
        )
    assert not (tmp_path / "S01.wav").exists()
