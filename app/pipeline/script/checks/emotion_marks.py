"""Pontos de atenção das marcas de emoção no `vp check` (ADR 063).

Os erros (marca desconhecida, sem fechar, uma dentro da outra, vazia) já saem de `narration_problems`. Aqui
ficam os avisos de estilo para o gate 2: marca com menos de `EMOTION_MIN_WORDS` palavras (cada corte reinicia
a entonação da voz) e mais de `EMOTION_MAX_PER_SCENE` marcas numa cena.
"""

from __future__ import annotations

from app.media.constants.narration_constants import NarrationConstants
from app.media.narration import emotion_segments, strip_pauses
from app.pipeline.models.check_report import CheckReport
from app.pipeline.schemas import ScenesManifest
from app.pipeline.script.models.checked_episode import CheckedEpisode


def emotion_attention(scenes: ScenesManifest) -> list[str]:
    """Uma linha por cena com marca curta demais ou marcas demais."""
    lines: list[str] = []
    for scene in scenes.scenes:
        marked = [(name, text) for name, text in emotion_segments(scene.narration) if name is not None]
        for name, text in marked:
            words = len(strip_pauses(text).split())
            if words < NarrationConstants.EMOTION_MIN_WORDS:
                lines.append(
                    f"marca de emoção: {scene.id}: <{name}> com {words} palavra(s); "
                    "marque a frase ou a oração inteira (cada corte reinicia a entonação)"
                )
        if len(marked) > NarrationConstants.EMOTION_MAX_PER_SCENE:
            lines.append(
                f"marca de emoção: {scene.id}: {len(marked)} marcas na cena (até "
                f"{NarrationConstants.EMOTION_MAX_PER_SCENE} soa natural)"
            )
    return lines


def check(episode: CheckedEpisode, report: CheckReport) -> None:
    if episode.scenes is not None:
        report.attention += emotion_attention(episode.scenes)
