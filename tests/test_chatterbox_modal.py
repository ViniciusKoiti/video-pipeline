"""Voz clonada numa GPU do Modal (ADR 024): o cliente com o protocolo do worker, sem rede e sem conta.

O teste de ponta a ponta sobe o cliente de verdade num subprocesso, com um pacote `modal` falso no caminho de
importação: o adapter, o processo e o protocolo são os de produção; só a chamada remota é trocada.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import wave
from pathlib import Path
from typing import Any

import pytest

from app.bootstrap import build_context
from app.providers.errors import ProviderError
from app.providers.tts.base import SpeechRequest
from app.providers.tts.chatterbox import ChatterboxTTS, modal_starter
from app.providers.tts.chatterbox_modal_client import handle, serve

REPO_ROOT = Path(__file__).resolve().parents[1]


def wav_bytes(frames: int = 2400) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(b"\x00\x00" * frames)
    return buffer.getvalue()


def reference(tmp_path: Path) -> Path:
    path = tmp_path / "voz.wav"
    path.write_bytes(wav_bytes(100))
    return path


def test_the_recording_never_goes_in_the_request_only_its_hash(tmp_path: Path) -> None:
    voice = reference(tmp_path)
    sent: list[dict[str, Any]] = []

    def call(job: dict[str, Any]) -> dict[str, Any]:
        sent.append(job)
        return {"ok": True, "seconds": 0.1, "wav": wav_bytes()}

    job = {"parts": ["Olá."], "language_id": "pt", "reference": str(voice),
           "out_path": str(tmp_path / "o.wav"), "pause_ms": 400, "exaggeration": 0.8, "cfg_weight": 0.3}
    assert handle(job, "referencia.wav", call) == {"ok": True, "seconds": 0.1}
    (remote,) = sent
    assert remote == {"parts": ["Olá."], "language_id": "pt", "pause_ms": 400, "exaggeration": 0.8,
                      "cfg_weight": 0.3, "reference_name": "referencia.wav",
                      "reference_hash": hashlib.sha256(voice.read_bytes()).hexdigest()[:12]}
    assert (tmp_path / "o.wav").read_bytes() == wav_bytes()


def test_a_remote_failure_comes_back_as_an_answer_and_the_client_goes_on(tmp_path: Path) -> None:
    voice = reference(tmp_path)
    answers = iter([{"ok": False, "error": "gravação diferente"},
                    {"ok": True, "seconds": 1, "wav": wav_bytes()}])
    out = io.StringIO()
    job = {"parts": ["a"], "language_id": "pt", "reference": str(voice), "out_path": str(tmp_path / "o.wav"),
           "pause_ms": 0}
    lines = [json.dumps(job), "", "não é json", json.dumps(job)]
    serve(lines, out, "referencia.wav", lambda _: next(answers))
    replies = [json.loads(line) for line in out.getvalue().splitlines()]
    assert replies[0] == {"ready": True}
    assert replies[1] == {"ok": False, "error": "gravação diferente"}
    assert replies[2]["ok"] is False and replies[2]["error"].startswith("JSONDecodeError")
    assert replies[3] == {"ok": True, "seconds": 1}


FAKE_MODAL = '''
import os


class _Generate:
    def remote(self, job):
        if os.environ.get("FAKE_MODAL_FAIL"):
            return {"ok": False, "error": "volume sem a gravação"}
        import io, wave
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(24000)
            wav.writeframes(b"\\x00\\x00" * 2400)
        with open(os.environ["FAKE_MODAL_LOG"], "a") as log:
            log.write(repr(sorted(job)) + "\\n")
        return {"ok": True, "seconds": 0.1, "wav": buffer.getvalue()}


class _Instance:
    generate = _Generate()


class Cls:
    @staticmethod
    def from_name(app, name):
        assert (app, name) == ("voz-dono", "Chatterbox")
        return lambda model_name: _Instance()
'''


@pytest.fixture
def fake_modal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    package = tmp_path / "fake" / "modal"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(FAKE_MODAL)
    log = tmp_path / "chamadas.log"
    monkeypatch.setenv("PYTHONPATH", str(package.parent))
    monkeypatch.setenv("FAKE_MODAL_LOG", str(log))
    return log


def cloud_tts(tmp_path: Path) -> ChatterboxTTS:
    return ChatterboxTTS(
        Path(sys.executable), reference(tmp_path), model="v3", language_ids={"pt-BR": "pt"}, pause_ms=400,
        start=modal_starter("voz-dono", "referencia.wav"), provider="chatterbox_modal", remote=True,
    )


def test_end_to_end_the_adapter_drives_the_real_client_process(tmp_path: Path, fake_modal: Path) -> None:
    tts = cloud_tts(tmp_path)
    try:
        result = tts.synthesize_speech(
            SpeechRequest(text="Meia lata, <short pause> quanto custa?", out_path=tmp_path / "S01.wav",
                          language="pt-BR", delivery="hook")
        )
    finally:
        tts.close()
    assert result.path.stat().st_size > 44 and result.model == "chatterbox-multilingual-v3"
    assert tts.info.name == "chatterbox_modal" and tts.info.remote
    sent = fake_modal.read_text()
    assert "reference_hash" in sent and "reference" not in sent.replace("reference_hash", "").replace(
        "reference_name", "")


def test_end_to_end_a_remote_refusal_is_a_provider_error(
    tmp_path: Path, fake_modal: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAKE_MODAL_FAIL", "1")
    tts = cloud_tts(tmp_path)
    try:
        with pytest.raises(ProviderError, match="volume sem a gravação"):
            tts.synthesize_speech(SpeechRequest(text="Olá.", out_path=tmp_path / "S01.wav", language="pt-BR"))
    finally:
        tts.close()


def test_the_cloud_voice_is_registered_free_and_remote(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(REPO_ROOT)
    context = build_context(REPO_ROOT, environ={"CHATTERBOX_REFERENCE": str(reference(tmp_path))})
    tts = context.tts_named("chatterbox_modal")
    assert tts.info.name == "chatterbox_modal" and tts.info.remote and tts.info.usd_per_call == 0
