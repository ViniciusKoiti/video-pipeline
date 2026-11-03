"""Processo do Chatterbox e seu protocolo JSON, compartilhados pelo worker local e o cliente do Modal."""

from __future__ import annotations

import json
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol

from app.providers.tts.constants.chatterbox_constants import ChatterboxConstants


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

