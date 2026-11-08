"""A pasta de falas e o narrador que a preenche (RF6, ADR 049): o que `montar_episodio.py` e `shorts_tec.py`
faziam cada um do seu jeito.

**`VoiceLibrary`** é só arquivos, nenhum provedor: o caminho de cada fala, se ela existe, as versões antigas
dela (mesmo começo de nome, outro hash) e a poda delas.

**`Narrator`** gera as falas que faltam com um `TTSProvider`:

- A chave do WAV vem do adapter (`TTSProvider.fingerprint`, ADR 041) e do texto que a voz lê (glossário
  aplicado). **Nos dois formatos o nome é o de hoje, mantido por decisão do dono** (as falas já aprovadas na
  escuta não são regeradas). No longo, a identidade do adapter sem os valores da entrega clonada
  (`|entrega:<nome>=<ênfase>,<cfg>` vira `|entrega:<nome>`). No Short, a identidade de um pedido sem texto
  (sem pausa nem fala longa) mais a entrega pelo nome, no formato antigo, só nas vozes clonadas. Os dois
  formatos são testados, com todas as entregas, contra as funções reais dos scripts.
- Gera só o que não existe; em lote quando o provedor oferece, com o fallback e a cota da ADR 041
  (`synthesize_requests`). O erro de uma fala vira `needs_review` dela e as outras seguem.
- **Uma fala nova só substitui a antiga depois de pronta:** o WAV é conferido (mede mais que zero) e só
  então as versões antigas são podadas. Falha, WAV inválido ou cota esgotada deixam o anterior utilizável
  (os scripts apagavam as antigas antes de gerar).
- Retomar é rodar de novo: o cache são os nomes dos arquivos, então um processo novo só pede o que falta.
- O TTS vem emprestado: quem o constrói o fecha (`closing_tts`).
"""

from __future__ import annotations

import glob
import hashlib
import math
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path

from app.errors import PipelineError
from app.media.probe import ProbeError
from app.media.speech_batches import synthesize_requests
from app.media.wav import wav_is_valid
from app.pipeline.constants.voice_constants import VoiceConstants
from app.pipeline.models.naming import Naming
from app.pipeline.models.planned_speech import PlannedSpeech
from app.pipeline.models.scene_outcome import SceneOutcome
from app.pipeline.models.speech_line import SpeechLine
from app.pipeline.models.status import Status
from app.pipeline.models.voice_key import VoiceKey
from app.providers.errors import InvalidOutput, ProviderError
from app.providers.tts.base import ReferencedTTS, SpeechRequest, TTSProvider

Outcome = SceneOutcome[Path]


class VoiceIncomplete(PipelineError, RuntimeError):
    """Faltou fala: a mensagem diz quais e por quê. As que ficaram prontas seguem na pasta."""


class VoiceLibrary:
    def __init__(self, folder: Path, naming: Naming) -> None:
        self.folder, self.naming = folder, naming

    def path(self, key: VoiceKey) -> Path:
        return self.folder / key.file_name(self.naming)

    def has(self, key: VoiceKey) -> bool:
        return wav_is_valid(self.path(key))

    def stale(self, key: VoiceKey) -> list[Path]:
        """As versões antigas desta fala: o mesmo começo de nome, outro hash. Nada de outra cena, outro
        provedor ou outro idioma."""
        stem = glob.escape(key.stem(self.naming))
        pattern = f"{stem}-{'?' * VoiceConstants.DIGEST_CHARS}.wav"
        return sorted(p for p in self.folder.glob(pattern) if p != self.path(key))

    def prune(self, key: VoiceKey) -> list[Path]:
        removed = self.stale(key)
        for path in removed:
            path.unlink()
        return removed


class Narrator:
    def __init__(
        self,
        tts: TTSProvider,
        language: str,
        library: VoiceLibrary,
        measure: Callable[[Path], float],
        respell: Callable[[str], str] = lambda text: text,
    ) -> None:
        self._tts, self._language, self._library = tts, language, library
        self._measure, self._respell = measure, respell  # `measure`: segundos do WAV (ffprobe nos scripts)

    def key(self, line: SpeechLine) -> VoiceKey:
        spoken = self._respell(line.text)
        request = SpeechRequest(
            text=spoken,
            out_path=self._library.folder / "x.wav",
            language=self._language,
            delivery=line.delivery,
        )
        return VoiceKey(line.id, self._tts.identity, self._language, self._fingerprint(request), spoken)

    def _fingerprint(self, request: SpeechRequest) -> str:
        if isinstance(self._tts, ReferencedTTS) and self._tts.scene_references:
            return self._tts.fingerprint(request)
        if self._library.naming is Naming.LONG:
            full = self._tts.fingerprint(request)
            if self._tts.identity in VoiceConstants.CLONED:  # o nome de hoje não leva os valores da entrega
                return VoiceConstants.DELIVERY_VALUES.sub(r"\1", full)
            return full
        base = self._tts.fingerprint(replace(request, text="", delivery=VoiceConstants.NEUTRAL))
        named = self._tts.identity in VoiceConstants.CLONED and request.delivery != VoiceConstants.NEUTRAL
        return base + (VoiceConstants.LEGACY_DELIVERY.format(name=request.delivery) if named else "")

    def input_hash(self, lines: Sequence[SpeechLine]) -> str:
        """Muda quando qualquer fala muda de texto, voz ou entrega: é o `input_hash` do estado da etapa."""
        names = []
        for line in lines:
            try:
                names.append(self.key(line).file_name(self._library.naming))
            except ProviderError as error:
                names.append(f"{line.id}|{line.delivery}|{line.text}|{error}")
        return "sha256:" + hashlib.sha256("\n".join(names).encode()).hexdigest()

    def plan(self, lines: Sequence[SpeechLine]) -> list[PlannedSpeech]:
        """Só as falas sem WAV (ou com um arquivo inválido no lugar dele)."""
        planned = []
        for line in lines:
            key = self.key(line)
            if not self._library.has(key):
                request = SpeechRequest(
                    text=key.spoken,
                    out_path=self._library.path(key),
                    language=self._language,
                    delivery=line.delivery,
                )
                planned.append(PlannedSpeech(line, key, request))
        return planned

    def synthesize(self, planned: Sequence[PlannedSpeech]) -> list[Outcome]:
        outcomes = synthesize_requests(self._tts, [p.request for p in planned])
        settled = []
        for item, outcome in zip(planned, outcomes, strict=True):
            if outcome.status is Status.COMPLETED:
                outcome = self._measured(item, outcome)
            if outcome.status is Status.COMPLETED:
                self._library.prune(item.key)  # só depois de a nova estar pronta e conferida
            settled.append(replace(outcome, scene_id=item.line.id))
        return settled

    def _measured(self, item: PlannedSpeech, outcome: Outcome) -> Outcome:
        path = item.request.out_path
        try:
            seconds = self._measure(path)
            valid = math.isfinite(seconds) and seconds > 0
        except ProbeError:
            valid = False
        if valid:
            return outcome
        path.unlink(missing_ok=True)
        detail = f"{path.name}: o WAV gerado não mede mais que zero"
        return SceneOutcome(outcome.scene_id, Status.NEEDS_REVIEW, reason=InvalidOutput.reason, detail=detail)

    def produce(self, lines: Sequence[SpeechLine]) -> list[Outcome]:
        """Uma saída por fala, na ordem: a que já existia, a gerada agora ou o motivo da falha."""
        valid, failed = [], {}
        for line in lines:
            try:
                self.key(line)
            except ProviderError as error:
                failed[line.id] = SceneOutcome[Path](
                    line.id, Status.NEEDS_REVIEW, reason=error.reason, detail=str(error)
                )
            else:
                valid.append(line)
        done = {o.scene_id: o for o in self.synthesize(self.plan(valid))}
        outcomes = []
        for line in lines:
            if line.id in failed:
                outcomes.append(failed[line.id])
                continue
            key = self.key(line)
            outcome = done.get(line.id) or SceneOutcome(
                line.id, Status.COMPLETED, value=self._library.path(key)
            )
            if outcome.status is Status.COMPLETED:
                outcome = replace(outcome, detail=key.fingerprint)
            outcomes.append(outcome)
        return outcomes

    @staticmethod
    def require(outcomes: Sequence[Outcome]) -> dict[str, Path]:
        """O WAV de cada fala, por id; se alguma falhou, `VoiceIncomplete` com o motivo de cada uma. As
        prontas ficam na pasta, e rodar de novo pede só as que faltam."""
        failed = [o for o in outcomes if o.status is not Status.COMPLETED or o.value is None]
        if failed:
            lines = "; ".join(f"{o.scene_id}: {o.reason}: {o.detail}" for o in failed)
            message = f"{len(failed)} fala(s) sem WAV ({lines}). As prontas ficam; rode de novo depois."
            raise VoiceIncomplete(message)
        return {o.scene_id: o.value for o in outcomes if o.value is not None}
