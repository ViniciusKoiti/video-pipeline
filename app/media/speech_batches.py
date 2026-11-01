"""Lote e fallback da voz (RF3, ADR 041): o que decide quantas chamadas um conjunto de falas custa.

- **Agrupamento** (`group_requests`): só cenas seguidas, com a mesma voz e o mesmo idioma, até o limite de
  caracteres do provedor; cena com pausa interna ou com glossário vai sozinha (ADR 015). A ordem não muda.
- **Fallback por cena:** só a recusa de corte do lote (`InvalidOutput`) manda gerar cena a cena. Qualquer
  outro erro de provedor vale para o grupo inteiro, sem repetir cena por cena: o adapter já tentou de novo
  o que era passageiro.
- **Cota esgotada** para tudo: as falas que ainda não foram tentadas ficam `needs_review` com o motivo, sem
  nova chamada. Cada fala volta como um `SceneOutcome` na ordem do pedido; `ProviderError` nunca sobe.
- **Nenhum WAV inválido sobra:** conferido o arquivo de cada sucesso; o que falhou e não existia antes
  é apagado.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from app.media.narration import has_pauses
from app.media.wav import wav_is_valid
from app.pipeline.models.scene_outcome import SceneOutcome
from app.pipeline.models.status import Status
from app.providers.errors import InvalidOutput, ProviderError, QuotaExhausted
from app.providers.tts.base import BatchTTS, SpeechRequest, TTSProvider

Outcome = SceneOutcome[Path]


def group_requests(requests: Sequence[SpeechRequest], limit: int) -> list[list[SpeechRequest]]:
    groups: list[list[SpeechRequest]] = []
    size, key = 0, None
    for request in requests:
        if has_pauses(request.text) or request.lexicon:
            groups.append([request])
            key = None
        elif groups and key == (request.voice, request.language) and size + len(request.text) <= limit:
            groups[-1].append(request)
            size += len(request.text)
        else:
            groups.append([request])
            size, key = len(request.text), (request.voice, request.language)
    return groups


def synthesize_requests(tts: TTSProvider, requests: Sequence[SpeechRequest]) -> list[Outcome]:
    existed = {r.out_path for r in requests if r.out_path.exists()}
    batch = tts if isinstance(tts, BatchTTS) else None
    groups = group_requests(requests, batch.max_batch_chars) if batch else [[r] for r in requests]
    outcomes: list[Outcome] = []
    exhausted = False
    for group in groups:
        got = [_skipped(r) for r in group] if exhausted else _run_group(tts, batch, group)
        outcomes += got
        exhausted = exhausted or any(o.reason == QuotaExhausted.reason for o in got)
    return [_settled(o, r, existed) for o, r in zip(outcomes, requests, strict=True)]


def _run_group(tts: TTSProvider, batch: BatchTTS | None, group: list[SpeechRequest]) -> list[Outcome]:
    if batch is not None and len(group) > 1:
        try:
            results = batch.synthesize_many(group)
            if [r.path for r in results] != [r.out_path for r in group]:
                raise ProviderError(tts.info.name, "o lote devolveu resultados fora dos pedidos")
            return [_done(r) for r in group]
        except InvalidOutput:
            pass  # a recusa de corte prevista: gera cena a cena
        except ProviderError as error:
            return [_failed(r, error) for r in group]
    outcomes: list[Outcome] = []
    for i, request in enumerate(group):
        try:
            tts.synthesize_speech(request)
        except ProviderError as error:
            outcomes.append(_failed(request, error))
            if isinstance(error, QuotaExhausted):
                return [*outcomes, *(_skipped(r) for r in group[i + 1 :])]
        else:
            outcomes.append(_done(request))
    return outcomes


def _done(request: SpeechRequest) -> Outcome:
    return SceneOutcome(request.out_path.name, Status.COMPLETED, value=request.out_path)


def _failed(request: SpeechRequest, error: ProviderError) -> Outcome:
    return SceneOutcome(request.out_path.name, Status.NEEDS_REVIEW, reason=error.reason, detail=str(error))


def _skipped(request: SpeechRequest) -> Outcome:
    detail = "não tentada: a cota esgotou antes nesta rodada"
    name = request.out_path.name
    return SceneOutcome(name, Status.NEEDS_REVIEW, reason=QuotaExhausted.reason, detail=detail)


def _settled(outcome: Outcome, request: SpeechRequest, existed: set[Path]) -> Outcome:
    """Sucesso só com WAV válido; o que falhou não deixa arquivo novo para trás."""
    if outcome.status is Status.COMPLETED and not wav_is_valid(request.out_path):
        outcome = SceneOutcome(
            outcome.scene_id, Status.NEEDS_REVIEW, reason=InvalidOutput.reason,
            detail=f"{request.out_path.name}: o áudio gerado não é um WAV válido",
        )
    if outcome.status is not Status.COMPLETED and request.out_path not in existed:
        request.out_path.unlink(missing_ok=True)
    return outcome
