"""As legendas de um episódio longo (RF7; eram `captions` e `word_captions` do `montar_episodio.py`).

- **Por frase** (#17, ADR 021): `captions.srt` com o tempo tirado dos WAVs; o arquivo é editável e só é
  refeito quando a fala muda (o anterior fica em `captions.old.srt`). Um SRT com intervalo inválido ou além
  do áudio é `CaptionProductionError` e para antes do render. `before_change` deixa o gate 4 aprovado
  recusar a troca antes de o arquivo ser tocado.
- **Palavra a palavra** (ADR 023): `captions.words.json`. Reconhecer exige o Whisper remoto (camada
  gratuita: só com pedido do dono na sessão) e é pedido por quem chama (`recognize`); sem pedido,
  reaproveita o arquivo que existe, e cena sem ele fica na legenda por frase. Uma parada do provedor no
  meio (cota, serviço) não perde as cenas já reconhecidas: ficam no arquivo e rodar de novo continua.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.errors import PipelineError
from app.media.captions import (
    SceneAudio,
    captions_key,
    episode_cues,
    parse_srt,
    review_hints,
    sync_captions,
    timing_problems,
)
from app.media.constants.captions_constants import CaptionsConstants
from app.media.constants.word_captions_constants import WordCaptionsConstants
from app.media.pauses import silences
from app.media.word_captions import Report, SceneSpeech, sync_words
from app.pipeline.models.captions_report import CaptionsReport
from app.pipeline.schemas import EpisodeScene
from app.providers.alignment.base import TimedWord
from app.providers.errors import ProviderError


class CaptionProductionError(PipelineError, ValueError):
    """Legenda que não pode seguir para o render; a mensagem diz o motivo."""


def write_captions(
    episode_dir: Path,
    scenes: list[EpisodeScene],
    wavs: dict[str, Path],
    total_ms: int,
    before_change: Callable[[str], None] | None = None,
) -> CaptionsReport:
    """Gera ou mantém `captions.srt` e confere o arquivo que vai para o render."""
    audio = [
        SceneAudio(
            start_ms=scene.start_ms,
            duration_ms=scene.duration_ms,
            narration=scene.narration,
            silences_ms=[(round(a * 1000), round(b * 1000)) for a, b in silences(wavs[scene.id])],
        )
        for scene in scenes
    ]
    cues, approximate = episode_cues(audio)
    key = captions_key([wavs[scene.id].name for scene in scenes])
    note = sync_captions(episode_dir, cues, key, before_change)
    found, problems = parse_srt((episode_dir / CaptionsConstants.CAPTIONS).read_text())
    problems += timing_problems(found, total_ms)
    if problems:
        raise CaptionProductionError(f"{CaptionsConstants.CAPTIONS}: " + "; ".join(problems))
    return CaptionsReport(note, len(found), approximate, tuple(review_hints(found)))


def write_word_captions(
    episode_dir: Path,
    scenes: list[EpisodeScene],
    recognize: Callable[[SceneSpeech], list[TimedWord]] | None,
    aligner_name: str,
) -> Report | None:
    """Palavras com tempo em `captions.words.json`; `recognize` só vem quando o dono pediu o reconhecimento.
    Sem pedido e sem o arquivo, não há o que fazer (`None`)."""
    path = episode_dir / WordCaptionsConstants.WORDS
    if recognize is None and not path.is_file():
        return None
    speech = [SceneSpeech(s.id, s.audio, s.narration, s.duration_ms) for s in scenes]
    try:
        return sync_words(path, speech, recognize, aligner_name)
    except ProviderError as error:
        raise CaptionProductionError(
            f"legenda palavra a palavra: {error.reason}: {error}. As cenas já reconhecidas "
            f"ficam em {WordCaptionsConstants.WORDS}; rode de novo depois."
        ) from error
