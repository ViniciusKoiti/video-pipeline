"""Onde conferir o áudio de um vídeo pronto (RF7; eram `cuts_from_episode`, `cuts_from_content` e
`expected_from_sfx` de `conferir_audio.py`): os cortes de cena e os momentos em que o plano pôs um efeito.

O earshot (`app/media/earshot.py`) mede a loudness como o YouTube mede, o pico real, a batida da trilha e,
em cada tempo que passamos aqui, se há um ataque de som perto dele.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.errors import PipelineError
from app.pipeline.constants.audio_review_constants import AudioReviewConstants
from app.pipeline.models.motion_content import MotionContent
from app.pipeline.models.sfx_kit import SfxKit
from app.pipeline.models.sfx_plan import SfxPlan


class AudioReviewError(PipelineError, RuntimeError):
    """A conferência não pode rodar: ambiente do earshot ausente, kit ausente ou máquina limitada."""


def cuts_from_episode(episode_json: Path) -> list[float]:
    """Os cortes de um vídeo longo: o `start_ms` de cada cena do `episode.json`, menos a primeira."""
    episode = json.loads(episode_json.read_text(encoding="utf-8"))
    return [round(scene["start_ms"] / 1000, 3) for scene in episode["scenes"]][1:]


def cuts_from_content(content: MotionContent) -> tuple[list[float], dict[str, float]]:
    """Os cortes de um Short (o começo de cada cena, menos a primeira) e o começo de cada cena por id."""
    starts = content.starts()
    return [round(t, 3) for t in list(starts.values())[1:]], starts


def expected_onsets(plan: SfxPlan, kit: SfxKit | None, starts: dict[str, float]) -> set[float]:
    """Onde o ataque de cada som colocado por deslocamento (começo da cena + `offset_s`, sem âncora de
    texto) tem de cair: o momento do plano menos o `sync.at` do kit mais o `onset` do som. Num pop é o próprio
    momento; num whoosh o ataque vem antes do pico, e é isso que o earshot ouve. Os ancorados na fala dependem
    do WAV e ficam fora desta conferência."""
    if kit is None:
        raise AudioReviewError("falta o SFX Kit em data/sfx/kit/ para ler o sync.at dos sons")
    moments = set()
    for cue in plan.cues:
        if cue.text is not None or cue.scene not in starts or cue.sound not in kit.sounds:
            continue
        sound = kit.sounds[cue.sound]
        onset = starts[cue.scene] + cue.offset_s - sound.sync_at + sound.onset
        if onset > AudioReviewConstants.MIN_ONSET_S:
            moments.add(round(onset, 3))
    return moments
