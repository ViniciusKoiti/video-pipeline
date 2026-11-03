"""Porta de narração. A duração do WAV é medida depois com ffprobe, nunca confiada ao adapter (§9).

Contrato (RF3, ADR 041):

- `identity` é a chave estável do cache de voz, no nome do WAV; `info.name` é só o nome de exibição (a
  chave `gemini` do cache vem de antes do nome `gemini_tts`, e continua).
- `fingerprint(request)` responde pelos parâmetros **efetivos** da síntese daquele pedido (voz, modelo,
  referência, pausa, entrega, agrupamento da fala longa): a síntese usa a mesma resolução, então a mesma
  entrada efetiva dá a mesma identidade, e mudar um parâmetro que muda a fala muda a identidade. O texto não
  entra: quem monta a chave do arquivo junta `fingerprint` e texto. Pedido que a síntese recusaria (idioma ou
  voz ausente, glossário não aceito) é recusado também aqui, com o mesmo erro.
- Escrita: o WAV do `out_path` só aparece inteiro e válido; falha deixa o que havia antes (`atomic_wav`).
- `BatchTTS` (opcional): várias cenas numa chamada. `synthesize_many` devolve um resultado por pedido, na
  ordem, com o `out_path` do pedido; exige uma voz e um idioma só; corte duvidoso é `InvalidOutput` (a
  única recusa que autoriza gerar cena a cena); qualquer outro erro vale para o lote inteiro.
- `Closeable` (opcional): quem constrói o TTS o fecha (`closing_tts`), também na exceção; quem o recebe do
  `Context` não fecha. `close()` é idempotente e o provedor pode ser usado de novo depois (reabre sob
  demanda).
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Protocol, runtime_checkable

from app.providers.base import ProviderInfo
from app.providers.tts.models.speech_request import SpeechRequest as SpeechRequest
from app.providers.tts.models.speech_result import SpeechResult as SpeechResult
from app.providers.tts.models.voice_reference import VoiceReference


class TTSProvider(Protocol):
    info: ProviderInfo
    identity: str  # chave estável do cache de voz, independente de `info.name`

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult: ...

    def fingerprint(self, request: SpeechRequest) -> str: ...


@runtime_checkable
class ReferencedTTS(Protocol):
    """Voz com referência consultável, inclusive quando a fala já está em cache."""

    scene_references: bool

    def reference_for(self, request: SpeechRequest) -> VoiceReference: ...


@runtime_checkable
class BatchTTS(Protocol):
    max_batch_chars: int  # soma dos textos de um lote, sem contar a cena única maior que o limite

    def synthesize_many(self, requests: Sequence[SpeechRequest]) -> list[SpeechResult]: ...


@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...


@contextmanager
def closing_tts(tts: TTSProvider) -> Iterator[TTSProvider]:
    """Fecha o TTS ao sair, com ou sem erro, se ele guarda recurso (um processo com o modelo carregado)."""
    try:
        yield tts
    finally:
        if isinstance(tts, Closeable):
            tts.close()
