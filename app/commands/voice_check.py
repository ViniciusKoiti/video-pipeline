"""`vp voice --conferir`: a conferência da fala pronta (ADR 062).

Ouve o WAV que vai ao vídeo de cada cena com o reconhecedor local (`speech_check` no `providers.toml`), grava
`voice/conferencia.json` e, se houver diferenças, a folha de escuta `voice/conferencia-escuta.wav` com os
trechos na ordem da lista. Não muda fala nenhuma: a nova tomada é
`vp voice <id> --voz-final --refazer <cenas>`.
"""

from __future__ import annotations

from app.errors import PipelineError
from app.media.listening_sheet import build_sheet
from app.media.pronunciation import load_glossary
from app.pipeline.atomic_files import write_atomic
from app.pipeline.constants.speech_review_constants import SpeechReviewConstants as Constants
from app.pipeline.models.heard_difference import HeardDifference
from app.pipeline.ports import Context
from app.pipeline.retention_clock import mmss
from app.pipeline.schemas import ScenesManifest
from app.pipeline.speech_review import review_speech
from app.pipeline.voice_timeline import voiced_paths


class VoiceCheckError(PipelineError, RuntimeError):
    """Falta a fala de alguma cena para conferir."""


def _line(number: int, difference: HeardDifference) -> str:
    heard = f'"{difference.heard}"' if difference.heard else "nada"
    spoken = f' (glossário: "{difference.spoken_as}")' if difference.spoken_as else ""
    where = f"{difference.scene_id} +{mmss(difference.start_ms / 1000)}"
    return f'{number:2d}. {where} {difference.kind}: "{difference.expected}"{spoken} -> ouvido {heard}'


def check_speech(context: Context, scenes: ScenesManifest, episode_id: str) -> int:
    store = context.store
    paths = voiced_paths(store, episode_id, [scene.id for scene in scenes.scenes])
    if paths is None:
        raise VoiceCheckError("falta a fala de alguma cena: rode o `vp voice` antes de conferir")
    folder = store.path(episode_id, "")
    review = review_speech(context.speech_checker, scenes, paths, load_glossary(folder), folder)
    write_atomic(folder / Constants.REPORT_FILE, (review.model_dump_json(indent=2) + "\n").encode())
    differences = review.differences
    count = len(differences)
    print(f"conferência ({review.recognizer}): {count} trecho(s) para ouvir; {Constants.REPORT_FILE}")
    for number, difference in enumerate(differences, start=1):
        print(_line(number, difference))
    if not differences:
        print("nenhuma diferença; o reconhecedor também erra: ouça os nomes próprios mesmo assim")
        return 0
    clips = [(paths[d.scene_id], d.start_ms, d.end_ms) for d in differences]
    build_sheet(clips, folder / Constants.SHEET_FILE, pad_ms=Constants.CLIP_PAD_MS, gap_ms=Constants.GAP_MS)
    scenes_to_redo = " ".join(dict.fromkeys(d.scene_id for d in differences))
    print(f"folha de escuta: {Constants.SHEET_FILE} (os trechos na ordem acima)")
    print(f"nova tomada do que soar errado: vp voice {episode_id} --voz-final --refazer {scenes_to_redo}")
    return 0
