"""Adapter Chatterbox Multilingual local: voz clonada de uma gravação de referência (MIT; ADR 016, proposta).

O modelo tem dependências fixadas que não entram no `uv.lock` deste projeto: roda num ambiente próprio, num
processo à parte (`chatterbox_worker.py`), como o Remotion roda no Node. O processo carrega o modelo uma vez e
atende uma cena por pedido; em CPU a fala sai dezenas de vezes mais devagar que o tempo real.

A gravação de referência é dado pessoal: fica fora do Git, no caminho do `.env` (`CHATTERBOX_REFERENCE`), e
nunca sai da máquina. Sem dicionário de fonemas: o `lexicon` do pedido é ignorado.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Protocol

from app.media.narration import split_pauses
from app.providers.base import ProviderInfo
from app.providers.errors import ModelUnavailable, ProviderError
from app.providers.tts.base import SpeechRequest, SpeechResult

WORKER = Path(__file__).with_name("chatterbox_worker.py")
MODEL_PREFIX = "chatterbox-multilingual-"
# Entrega da fala (ADR 022): padrão do modelo na fala neutra; ênfase alta e cfg baixo no chamado.
DEFAULT_DELIVERY: dict[str, dict[str, float]] = {
    "neutral": {"exaggeration": 0.5, "cfg_weight": 0.5},
    "hook": {"exaggeration": 0.8, "cfg_weight": 0.3},
}


def reference_hash(reference: Path) -> str:
    """Entra na chave de cache da fala: trocar a gravação de referência troca a voz."""
    return hashlib.sha256(reference.read_bytes()).hexdigest()[:12]


class Worker(Protocol):
    def ask(self, job: Mapping[str, Any]) -> dict[str, Any]: ...


class SubprocessWorker:
    """O processo do modelo: uma linha de JSON por pedido, uma linha por resposta."""

    def __init__(self, python: Path, model: str, num_threads: int) -> None:
        # Avisos e barras de progresso do modelo; lido só em falha e aberto enquanto o processo vive.
        self._log = tempfile.TemporaryFile()  # noqa: SIM115
        self._process = subprocess.Popen(
            [str(python), str(WORKER), model, str(num_threads)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._log, text=True, encoding="utf-8",
        )
        ready = self._read()
        if not ready.get("ready"):
            raise RuntimeError(f"o processo do modelo não ficou pronto: {ready}")

    def _read(self) -> dict[str, Any]:
        assert self._process.stdout is not None
        line = self._process.stdout.readline()
        if not line:
            code = self._process.wait(timeout=30)
            self._log.seek(0)
            last = self._log.read().decode("utf-8", "replace").strip().splitlines()[-1:]
            raise RuntimeError(f"o processo do modelo terminou (código {code}): {' '.join(last)}")
        answer: dict[str, Any] = json.loads(line)
        return answer

    def ask(self, job: Mapping[str, Any]) -> dict[str, Any]:
        assert self._process.stdin is not None
        self._process.stdin.write(json.dumps(job, ensure_ascii=False) + "\n")
        self._process.stdin.flush()
        return self._read()

    def close(self) -> None:
        if self._process.poll() is None:
            assert self._process.stdin is not None
            self._process.stdin.close()
            self._process.wait(timeout=30)


class ChatterboxTTS:
    def __init__(
        self,
        python: Path | None,
        reference: Path | None,
        *,
        model: str = "v3",
        language_ids: Mapping[str, str],
        num_threads: int = 12,
        pause_ms: int = 400,
        delivery: Mapping[str, Mapping[str, float]] | None = None,
        start: Callable[[Path, str, int], Worker] = SubprocessWorker,
    ) -> None:
        self.info = ProviderInfo("chatterbox", remote=False)
        # Entrega da fala (ADR 022): ênfase e cfg por nome; entrega desconhecida cai na neutra.
        self._delivery = {name: dict(params) for name, params in (delivery or DEFAULT_DELIVERY).items()}
        self._python = python  # o Python do ambiente em que o Chatterbox está instalado
        self._reference = reference  # gravação da voz a clonar
        self._model = model
        self._language_ids = dict(language_ids)  # idioma do episódio -> código do modelo ("pt-BR" -> "pt")
        self._num_threads = num_threads
        self._pause_ms = pause_ms  # silêncio no lugar de cada `<short pause>` da narração (ADR 015)
        self._start = start
        self._worker: Worker | None = None

    def _ready(self) -> tuple[Worker, Path]:
        if self._python is None or not self._python.is_file():
            raise ModelUnavailable(self.info.name, "ambiente do modelo ausente (CHATTERBOX_PYTHON no .env)")
        if self._reference is None or not self._reference.is_file():
            raise ModelUnavailable(self.info.name, "gravação de referência ausente (CHATTERBOX_REFERENCE)")
        if self._worker is None:
            try:
                self._worker = self._start(self._python, self._model, self._num_threads)
            except (OSError, RuntimeError, ValueError) as error:
                raise ModelUnavailable(self.info.name, f"o modelo não carregou: {error}") from error
        return self._worker, self._reference

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        language_id = self._language_ids.get(request.language)
        if language_id is None:
            raise ModelUnavailable(self.info.name, f"sem código de idioma para {request.language!r}")
        worker, reference = self._ready()
        request.out_path.parent.mkdir(parents=True, exist_ok=True)
        params = self._delivery.get(request.delivery) or self._delivery.get("neutral") or {}
        job = {
            "parts": split_pauses(request.text) or [request.text],
            "language_id": language_id,
            "reference": str(reference),
            "out_path": str(request.out_path),
            "pause_ms": self._pause_ms,
            "exaggeration": params.get("exaggeration", 0.5),
            "cfg_weight": params.get("cfg_weight", 0.5),
        }
        try:
            answer = worker.ask(job)
        except (OSError, RuntimeError, ValueError) as error:
            self._worker = None  # o próximo pedido sobe o processo de novo
            raise ProviderError(self.info.name, f"o processo do modelo falhou: {error}") from error
        if not answer.get("ok") or not request.out_path.is_file():
            reason = answer.get("error") or "nenhum áudio gerado para o texto"
            raise ProviderError(self.info.name, str(reason))
        voice = f"clone:{reference_hash(reference)}"
        return SpeechResult(path=request.out_path, model=MODEL_PREFIX + self._model, voice=voice)

    def close(self) -> None:
        close = getattr(self._worker, "close", None)
        if close is not None:
            close()
        self._worker = None
