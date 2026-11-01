"""Adapter Chatterbox Multilingual local: voz clonada de uma gravação de referência (MIT; ADR 016, proposta).

O modelo tem dependências fixadas que não entram no `uv.lock` deste projeto: roda num ambiente próprio, num
processo à parte (`chatterbox_worker.py`), como o Remotion roda no Node. O processo carrega o modelo uma vez e
atende uma cena por pedido; em CPU a fala sai dezenas de vezes mais devagar que o tempo real.

A gravação de referência é dado pessoal: fica fora do Git, no caminho do `.env` (`CHATTERBOX_REFERENCE`), e
nunca sai da máquina. Sem dicionário de fonemas: o `lexicon` do pedido é ignorado.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Protocol

from app.media.narration import has_pauses, split_pauses
from app.providers.base import ProviderInfo
from app.providers.errors import ModelUnavailable, ProviderError
from app.providers.tts.base import SpeechRequest, SpeechResult
from app.providers.tts.chatterbox_text import join_wavs as join_wavs  # reexportados: imports de antes
from app.providers.tts.chatterbox_text import reference_hash as reference_hash
from app.providers.tts.chatterbox_text import split_long as split_long
from app.providers.tts.constants.chatterbox_constants import ChatterboxConstants
from app.providers.tts.files import atomic_wav

# A mesma fala numa GPU do Modal (ADR 024): um cliente com o protocolo do worker.


# O Chatterbox gera no máximo 1.000 tokens de fala por chamada (`max_new_tokens` fixo no `generate`), uns
# 40 s: passou disso, a fala sai cortada sem erro. A fala longa vai em grupos de frases até este tamanho, uma
# chamada por grupo, com um silêncio curto entre eles; as `<short pause>` seguem com o `pause_ms` (ADR 015).


# Entrega da fala (ADR 022): padrão do modelo na fala neutra; ênfase alta e cfg baixo no chamado.


class Worker(Protocol):
    def ask(self, job: Mapping[str, Any]) -> dict[str, Any]: ...


class SubprocessWorker:
    """O processo do modelo: uma linha de JSON por pedido, uma linha por resposta."""

    def __init__(
        self, python: Path, model: str, num_threads: int, *, command: list[str] | None = None
    ) -> None:
        # Avisos e barras de progresso do modelo; lido só em falha e aberto enquanto o processo vive.
        self._log = tempfile.TemporaryFile()  # noqa: SIM115
        self._process = subprocess.Popen(
            command or [str(python), str(ChatterboxConstants.WORKER), model, str(num_threads)],
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
        provider: str = "chatterbox",
        remote: bool = False,
    ) -> None:
        # `chatterbox_modal` (ADR 024): o mesmo adapter com a síntese numa GPU do Modal; muda só o processo.
        self.info = ProviderInfo(provider, remote=remote)
        self.identity = provider  # local e Modal têm chaves de cache separadas, como os WAVs de hoje
        # Entrega da fala (ADR 022): ênfase e cfg por nome; entrega desconhecida cai na neutra.
        self._delivery = {
            name: dict(params) for name, params in (delivery or ChatterboxConstants.DEFAULT_DELIVERY).items()
        }
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
            where = "a CLI do Modal (uv tool install modal)" if self.info.remote else "CHATTERBOX_PYTHON"
            raise ModelUnavailable(self.info.name, f"ambiente do modelo ausente ({where})")
        if self._reference is None or not self._reference.is_file():
            raise ModelUnavailable(self.info.name, "gravação de referência ausente (CHATTERBOX_REFERENCE)")
        if self._worker is None:
            try:
                self._worker = self._start(self._python, self._model, self._num_threads)
            except (OSError, RuntimeError, ValueError) as error:
                raise ModelUnavailable(self.info.name, f"o modelo não carregou: {error}") from error
        return self._worker, self._reference

    def _language_id(self, request: SpeechRequest) -> str:
        language_id = self._language_ids.get(request.language)
        if language_id is None:
            raise ModelUnavailable(self.info.name, f"sem código de idioma para {request.language!r}")
        return language_id

    def _delivery_params(self, delivery: str) -> tuple[str, float, float]:
        """(entrega efetiva, exaggeration, cfg_weight): entrega desconhecida cai na neutra (ADR 022).
        É a única resolução, usada pela síntese e pela identidade do cache."""
        named = self._delivery.get(delivery)
        used = delivery if named is not None else "neutral"
        params = named or self._delivery.get("neutral") or {}
        default = ChatterboxConstants.NEUTRAL_DEFAULT
        return used, params.get("exaggeration", default[0]), params.get("cfg_weight", default[1])

    def fingerprint(self, request: SpeechRequest) -> str:
        """`<nome>|<modelo>|<código do idioma>|<hash da referência>` mais, quando valem para o pedido:
        `|pausa<ms>` (texto com pausa), `|entrega:<nome>=<exaggeration>,<cfg_weight>` (entrega não neutra
        definida), `|neutro=<exaggeration>,<cfg_weight>` (parâmetros da neutra, usada também como fallback,
        só se diferem do padrão do modelo), `|frases<N>` (fala longa, em grupos de frases) e `|v<N>` (versão
        do corte e junção, só acima de 1). Os nomes de WAV de antes seguem válidos, salvo a entrega não
        neutra, que antes não levava os valores (ADR 041)."""
        language_id = self._language_id(request)
        reference = self._reference_path()
        text = [f"|pausa{self._pause_ms}"] if has_pauses(request.text) else []
        used, exaggeration, cfg_weight = self._delivery_params(request.delivery)
        pair = f"{exaggeration:g},{cfg_weight:g}"
        if used != "neutral":
            text.append(f"|entrega:{used}={pair}")
        elif (exaggeration, cfg_weight) != ChatterboxConstants.NEUTRAL_DEFAULT:
            text.append(f"|neutro={pair}")
        parts = split_pauses(request.text) or [request.text]
        if any(len(part) > ChatterboxConstants.MAX_PART_CHARS for part in parts):
            text.append(f"|frases{ChatterboxConstants.MAX_PART_CHARS}")
        if ChatterboxConstants.SPEECH_VERSION > 1:
            text.append(f"|v{ChatterboxConstants.SPEECH_VERSION}")
        base = f"{self.identity}|{self._model}|{language_id}|{reference_hash(reference)}"
        return base + "".join(text)

    def _reference_path(self) -> Path:
        if self._reference is None or not self._reference.is_file():
            raise ModelUnavailable(self.info.name, "gravação de referência ausente (CHATTERBOX_REFERENCE)")
        return self._reference

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        language_id = self._language_id(request)
        worker, reference = self._ready()
        _, exaggeration, cfg_weight = self._delivery_params(request.delivery)
        base = {
            "language_id": language_id,
            "reference": str(reference),
            "exaggeration": exaggeration,
            "cfg_weight": cfg_weight,
        }
        parts = split_pauses(request.text) or [request.text]
        groups = [split_long(part) or [part] for part in parts]
        with atomic_wav(request.out_path, self.info.name) as partial:
            if all(len(group) == 1 for group in groups):
                self._ask(worker, {**base, "parts": parts, "out_path": str(partial),
                                   "pause_ms": self._pause_ms}, partial)
            else:
                # Fala longa (mais que ~40 s numa chamada): um pedido por trecho entre pausas, cada um com os
                # grupos de frases; os trechos se juntam aqui com o silêncio das pausas.
                with tempfile.TemporaryDirectory(dir=request.out_path.parent) as folder:
                    pieces = []
                    for i, group in enumerate(groups):
                        piece = Path(folder) / f"trecho-{i:02d}.wav"
                        self._ask(worker, {**base, "parts": group, "out_path": str(piece),
                                           "pause_ms": ChatterboxConstants.SENTENCE_GAP_MS}, piece)
                        pieces.append(piece)
                    join_wavs(pieces, self._pause_ms, partial)
        voice = f"clone:{reference_hash(reference)}"
        return SpeechResult(
            path=request.out_path, model=ChatterboxConstants.MODEL_PREFIX + self._model, voice=voice
        )

    def _ask(self, worker: Worker, job: Mapping[str, Any], out_path: Path) -> None:
        try:
            answer = worker.ask(job)
        except (OSError, RuntimeError, ValueError) as error:
            self._worker = None  # o próximo pedido sobe o processo de novo
            raise ProviderError(self.info.name, f"o processo do modelo falhou: {error}") from error
        if not answer.get("ok") or not out_path.is_file():
            reason = answer.get("error") or "nenhum áudio gerado para o texto"
            raise ProviderError(self.info.name, str(reason))

    def close(self) -> None:
        close = getattr(self._worker, "close", None)
        if close is not None:
            close()
        self._worker = None


def modal_starter(app: str, reference_name: str) -> Callable[[Path, str, int], Worker]:
    """O processo do cliente do Modal (ADR 024): `python` é o da CLI do Modal, que tem o pacote e o token."""

    def start(python: Path, model: str, num_threads: int) -> Worker:
        command = [str(python), str(ChatterboxConstants.MODAL_CLIENT), app, model, reference_name]
        return SubprocessWorker(python, model, num_threads, command=command)

    return start
