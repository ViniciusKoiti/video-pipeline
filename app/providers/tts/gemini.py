"""Adapter Gemini TTS na camada gratuita (ADR 012): `POST /v1beta/interactions`, uma fala por chamada.

- A chave vai só no cabeçalho `x-goog-api-key` e nunca aparece em erro nem em log (§2.7).
- A camada gratuita aceita poucas chamadas por minuto (3 no `gemini-3.8-flash-tts`, erro 429 visto em
  2026-09-29): o adapter espaça as chamadas. Falha passageira (429, 500, 503 "high demand", tempo esgotado ou
  rede) espera o intervalo e tenta de novo uma vez; na segunda, 429 vira `QuotaExhausted` e o resto,
  `ProviderError` (a cena fica pendente, §2.1). Nunca troca de modelo sozinho: 404 vira `ModelUnavailable`.
- O texto é lido ao pé da letra; a direção de fala vai em `speech_metadata.style`, por idioma.
- Sem dicionário de fonemas: um glossário no pedido é erro, em vez de ser ignorado em silêncio.
- A resposta é WAV com cabeçalho RIFF (24 kHz, mono, 16 bits), gravado como veio.
"""

from __future__ import annotations

import base64
import time
from collections.abc import Callable, Mapping
from typing import Any

from app.providers.base import ProviderInfo
from app.providers.errors import InvalidOutput, ModelUnavailable, ProviderError, QuotaExhausted
from app.providers.http import AuthPost, TransportError, post_json_with_headers
from app.providers.tts.base import SpeechRequest, SpeechResult

API = "https://generativelanguage.googleapis.com/v1beta/interactions"
TIMEOUT_S = 90.0  # a fala mais longa do teste (188 caracteres) levou 27,5 s
TRANSIENT = frozenset({429, 500, 503})  # e status None: tempo esgotado ou rede
MARGIN_S = 1.0  # folga sobre 60 / chamadas por minuto


class GeminiTTS:
    def __init__(
        self,
        api_key: str,
        *,
        model: str,
        voices: Mapping[str, str],
        styles: Mapping[str, str],
        requests_per_minute: int,
        post: AuthPost = post_json_with_headers,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.info = ProviderInfo("gemini_tts", remote=True)  # camada gratuita: custo zero por chamada (§2.1)
        self._key = api_key
        self._model = model
        self._voices = dict(voices)  # idioma -> voz (ex.: {"pt-BR": "Charon"})
        self._styles = dict(styles)  # idioma -> direção de fala
        self._interval = 60 / requests_per_minute + MARGIN_S
        self._post = post
        self._clock = clock
        self._sleep = sleep
        self._last_call: float | None = None

    def voice_for(self, request: SpeechRequest) -> str:
        voice = request.voice or self._voices.get(request.language)
        if voice is None:
            raise ModelUnavailable(self.info.name, f"sem voz configurada para o idioma {request.language!r}")
        return voice

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult:
        if request.lexicon:
            raise ProviderError(self.info.name, "glossário de fonemas não é aceito pelo Gemini TTS (ADR 012)")
        voice = self.voice_for(request)
        content: dict[str, Any] = {"type": "text", "text": request.text}
        style = self._styles.get(request.language)
        if style:
            content["annotations"] = [{"type": "speech_metadata", "style": style}]
        body = {
            "model": self._model,
            "input": [{"type": "user_input", "content": [content]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": voice}]},
        }
        audio = self._audio(self._call(body))
        request.out_path.parent.mkdir(parents=True, exist_ok=True)
        request.out_path.write_bytes(audio)
        return SpeechResult(path=request.out_path, model=self._model, voice=voice)

    def _call(self, body: Mapping[str, Any]) -> dict[str, Any]:
        for attempt in (1, 2):
            self._wait()
            try:
                return self._post(API, body, {"x-goog-api-key": self._key}, TIMEOUT_S)
            except TransportError as error:
                if attempt == 1 and (error.status is None or error.status in TRANSIENT):
                    continue  # limite por minuto, serviço sobrecarregado ou rede: espera e tenta uma vez mais
                if error.status == 429:
                    raise QuotaExhausted(self.info.name, "cota da camada gratuita esgotada") from None
                if error.status == 404:
                    raise ModelUnavailable(self.info.name, f"modelo {self._model} indisponível") from None
                raise ProviderError(self.info.name, str(error)) from None
        raise AssertionError("inalcançável")

    def _wait(self) -> None:
        now = self._clock()
        if self._last_call is not None:
            remaining = self._interval - (now - self._last_call)
            if remaining > 0:
                self._sleep(remaining)
                now += remaining
        self._last_call = now

    def _audio(self, response: Mapping[str, Any]) -> bytes:
        blocks = [
            content
            for step in response.get("steps", [])
            if step.get("type") == "model_output"
            for content in step.get("content", [])
            if content.get("type") == "audio"
        ]
        if not blocks:
            raise InvalidOutput(self.info.name, "resposta sem áudio")
        audio = base64.b64decode(blocks[-1].get("data", ""))
        if audio[:4] != b"RIFF":
            raise InvalidOutput(self.info.name, "áudio sem cabeçalho WAV")
        return audio
