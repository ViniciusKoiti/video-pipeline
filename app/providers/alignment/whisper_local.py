"""Palavras com tempo pelo Whisper local, via `transformers` (ADR 062).

Roda na CPU, sem rede: o modelo vem do cache do Hugging Face, baixado uma vez pelo dono (`uv run hf download
openai/whisper-small`). Sem ele, para com o comando de download, sem baixar nada sozinho. Serve à conferência
da fala depois da voz (`vp voice --conferir`). O `prompt` é ignorado de propósito: o texto esperado
"corrigiria" o nome mal pronunciado, e a conferência quer ouvir o que a voz disse.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import cached_property
from pathlib import Path
from typing import Any

from app.providers.alignment.base import TimedWord
from app.providers.alignment.constants.whisper_local_constants import WhisperLocalConstants as Constants
from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput, ModelUnavailable

Recognizer = Callable[..., dict[str, Any]]  # o pipeline do transformers: (caminho, **opções) -> resultado


def _load_pipeline(model: str, num_threads: int) -> Recognizer:
    import torch
    from transformers import pipeline

    torch.set_num_threads(num_threads)
    try:
        return pipeline(Constants.TASK, model=model, device="cpu")  # type: ignore[call-overload,no-any-return]
    except OSError as error:  # modelo fora do cache com HF_HUB_OFFLINE=1
        hint = Constants.DOWNLOAD_HINT.format(model=model)
        raise ModelUnavailable("whisper_local", f"{model} não está no cache; {hint}") from error


class WhisperLocalWordAligner:
    def __init__(
        self,
        *,
        model: str,
        num_threads: int = 8,
        chunk_length_s: float = 30.0,
        load: Callable[[str, int], Recognizer] = _load_pipeline,
    ) -> None:
        self.info = ProviderInfo("whisper_local", remote=False)
        self._model, self._threads, self._chunk = model, num_threads, chunk_length_s
        self._load = load

    @cached_property
    def _recognizer(self) -> Recognizer:
        return self._load(self._model, self._threads)

    def recognize_words(self, audio: Path, language: str, prompt: str = "") -> list[TimedWord]:
        code = language.split("-")[0]
        options: dict[str, Any] = {"task": "transcribe"}
        if code in Constants.LANGUAGES:
            options["language"] = Constants.LANGUAGES[code]
        result = self._recognizer(
            str(audio), return_timestamps="word", chunk_length_s=self._chunk, generate_kwargs=options
        )
        chunks = result.get("chunks", [])
        return [_word(chunk, audio) for chunk in chunks if str(chunk.get("text", "")).strip()]


def _word(chunk: dict[str, Any], audio: Path) -> TimedWord:
    start, end = chunk.get("timestamp", (None, None))
    if start is None:
        raise InvalidOutput("whisper_local", f"palavra sem tempo em {audio.name}: {chunk!r}")
    end = start if end is None else end
    return TimedWord(str(chunk["text"]).strip(), round(start * 1000), round(end * 1000))
