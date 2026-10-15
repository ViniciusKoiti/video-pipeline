"""Palavras com tempo pelo Whisper da Groq, na camada gratuita (ADR 023).

Envia o WAV de uma cena e recebe as palavras reconhecidas com início e fim. O áudio sai da máquina: só roda
quando o dono pede na sessão (`montar_episodio.py --legenda-palavra`, §14). A chave fica no `.env`
(`GROQ_API_KEY`) e vai no cabeçalho, nunca na URL (§2.7).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.providers.alignment.base import TimedWord
from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput, ModelUnavailable, ProviderError, QuotaExhausted
from app.providers.http import MultipartPost, TransportError, post_multipart

URL = "https://api.groq.com/openai/v1/audio/transcriptions"
PROMPT_CHARS = 600  # o Whisper só usa os últimos ~224 tokens do prompt


class GroqWordAligner:
    def __init__(
        self, api_key: str, *, model: str, timeout_s: float = 120.0, post: MultipartPost = post_multipart
    ) -> None:
        self.info = ProviderInfo("groq", remote=True)
        self._key = api_key
        self._model = model
        self._timeout = timeout_s
        self._post = post

    def recognize_words(self, audio: Path, language: str, prompt: str = "") -> list[TimedWord]:
        fields = {
            "model": self._model,
            "language": language.split("-")[0],  # o Whisper usa ISO 639-1: pt-BR -> pt
            "response_format": "verbose_json",
            "timestamp_granularities[]": "word",
            "temperature": "0",
        }
        if prompt:
            fields["prompt"] = prompt[-PROMPT_CHARS:]
        try:
            auth = {"Authorization": f"Bearer {self._key}"}
            data = self._post(URL, fields, {"file": audio}, auth, self._timeout)
        except TransportError as error:
            raise _provider_error(error) from None
        return _words(data, audio.name)


def _provider_error(error: TransportError) -> ProviderError:
    if error.status == 429:
        return QuotaExhausted("groq", f"limite da camada gratuita ({error})")
    if error.status == 404 or (error.status == 400 and "model" in str(error).lower()):
        return ModelUnavailable("groq", str(error))
    return ProviderError("groq", str(error))


def _words(data: dict[str, Any], name: str) -> list[TimedWord]:
    raw = data.get("words")
    if not isinstance(raw, list) or not raw:
        raise InvalidOutput("groq", f"{name}: a resposta não trouxe palavras com tempo")
    words = []
    for item in raw:
        try:
            text = str(item["word"]).strip()
            start, end = round(float(item["start"]) * 1000), round(float(item["end"]) * 1000)
        except (KeyError, TypeError, ValueError):
            raise InvalidOutput("groq", f"{name}: palavra sem texto ou tempo: {item!r}"[:200]) from None
        if text:
            words.append(TimedWord(text, start, max(end, start)))
    return words
