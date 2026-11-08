"""O estado da voz no `manifest.json` (RF6, ADR 052): o relatório por cena que sobrevive ao processo.

`produce_with_state` roda o `Narrator` com o episódio travado e grava, no fim, um registro por fala: pronta
(com o WAV) ou pendente (com o motivo: `quota_exhausted`, `invalid_output`...). A etapa fica `completed`
quando todas estão prontas, `needs_review` quando falta alguma (produção incompleta, `pending_scenes`) e
`failed`, com a mensagem, quando um erro que não é de provedor derruba a rodada (a exceção sobe, como no
`run_scenes`).

Retomar continua sendo rodar de novo: o que decide o que gerar são os nomes dos arquivos (a biblioteca), e o
estado diz, a quem chegar depois, o que ficou para trás. `voice_pending` o lê e confere se os WAVs registrados
ainda existem: é o que o `vp status` mostra.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from app.media.constants.voice_level_constants import VoiceLevelConstants
from app.media.models.voice_polish import VoicePolish
from app.media.voice_level import VoiceLevelError, level_policy, level_voice
from app.pipeline.models.scene_outcome import SceneOutcome
from app.pipeline.models.scene_record import SceneRecord
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.models.step_state import StepState
from app.pipeline.ports import ManifestStore
from app.pipeline.schemas import Status, Step
from app.pipeline.state import load_state, output_is_intact, save_step
from app.pipeline.voice import Narrator

Outcome = SceneOutcome[Path]


def _level(outcomes: list[Outcome], polish: VoicePolish | None) -> list[Outcome]:
    result = []
    for outcome in outcomes:
        if outcome.status is not Status.COMPLETED or outcome.value is None:
            result.append(outcome)
            continue
        try:
            wav = level_voice(outcome.value, polish)
        except VoiceLevelError as error:
            result.append(SceneOutcome[Path](
                outcome.scene_id, Status.NEEDS_REVIEW,
                reason=VoiceLevelConstants.REASON, detail=str(error),
            ))
        else:
            result.append(replace(
                outcome, value=wav, detail=f"{outcome.detail}|{level_policy(polish)}"
            ))
    return result


def _record(outcome: Outcome, folder: Path) -> SceneRecord:
    if outcome.status is Status.COMPLETED and outcome.value is not None:
        return SceneRecord(
            status=Status.COMPLETED, outputs=[outcome.value.relative_to(folder).as_posix()],
            detail=outcome.detail,
        )
    return SceneRecord(status=Status.NEEDS_REVIEW, reason=outcome.reason, detail=outcome.detail)


def save_voice_state(
    store: ManifestStore, episode_id: str, input_hash: str, outcomes: Sequence[Outcome], now: datetime
) -> StepState:
    """Grava o relatório por cena. Quem chama já segura o lock do episódio."""
    folder = store.path(episode_id, "")
    records = {outcome.scene_id: _record(outcome, folder) for outcome in outcomes}
    state = load_state(store, episode_id)
    incomplete = any(r.status is not Status.COMPLETED for r in records.values())
    step = StepState(
        status=Status.NEEDS_REVIEW if incomplete else Status.COMPLETED,
        input_hash=input_hash,
        outputs=[name for record in records.values() for name in record.outputs],
        started_at=state.get(Step.VOICE).started_at or now,
        finished_at=now,
        scenes=records,
    )
    save_step(store, state, Step.VOICE, step)
    return step


def _save_failure(
    store: ManifestStore, episode_id: str, input_hash: str, error: Exception, now: datetime
) -> None:
    state = load_state(store, episode_id)
    previous = state.get(Step.VOICE)
    # o que já estava pronto para esta entrada segue registrado
    kept = previous.scenes if previous.input_hash == input_hash else {}
    failed = StepState(
        status=Status.FAILED,
        input_hash=input_hash,
        error=f"erro_inesperado: {error}"[:500],
        started_at=previous.started_at or now,
        finished_at=now,
        scenes=kept,
    )
    save_step(store, state, Step.VOICE, failed)


def produce_with_state(
    narrator: Narrator, store: ManifestStore, episode_id: str, lines: Sequence[SpeechLine], *, now: datetime,
    level: bool = False, polish: VoicePolish | None = None,
) -> list[Outcome]:
    """`Narrator.produce` com o episódio travado e o relatório por cena gravado no fim. Erro que não é de
    provedor fica registrado como `failed` e sobe; não aninhar `store.lock` dentro da geração."""
    digest = narrator.input_hash(lines)
    if level:
        digest = "sha256:" + hashlib.sha256(f"{digest}|{level_policy(polish)}".encode()).hexdigest()
    with store.lock(episode_id):
        try:
            outcomes = narrator.produce(lines)
            if level:
                outcomes = _level(outcomes, polish)
        except Exception as error:
            _save_failure(store, episode_id, digest, error, now)
            raise
        save_voice_state(store, episode_id, digest, outcomes, now)
        return outcomes


def voice_pending(store: ManifestStore, episode_id: str) -> list[str]:
    """O que a voz deixou para trás, pelo estado gravado: falas pendentes com o motivo, WAV registrado que
    sumiu e rodada que falhou. Sem estado (voz que não passou por aqui), nada."""
    state = load_state(store, episode_id).get(Step.VOICE)
    items = []
    for scene_id, record in state.scenes.items():
        if record.status is not Status.COMPLETED:
            items.append(f"voz {scene_id} ({record.reason or 'pendente'})")
        elif any(not output_is_intact(store.path(episode_id, name)) for name in record.outputs):
            items.append(f"voz {scene_id} (WAV ausente)")
    if state.status is Status.FAILED:
        items.append(f"voz (rodada falhou: {state.error})")
    return items
