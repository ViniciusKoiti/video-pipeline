"""Nova tomada de cenas escolhidas (`vp voice --refazer`, ADR 062).

O nome do WAV vem do texto e da voz (ADR 049): o mesmo pedido acharia a fala antiga e não geraria outra. Para
pedir outra tomada, o WAV bruto da cena e as cópias dele (nivelada e com pausas) vão para
`voice/tomadas-recusadas/`; nada é apagado. A rodada seguinte do `vp voice` gera a fala que falta. A cópia
nivelada nova tem outro nome (o hash do conteúdo muda), e a legenda é refeita no próximo render.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from app.errors import PipelineError
from app.pipeline.constants.voice_retake_constants import VoiceRetakeConstants as Constants


class RetakeError(PipelineError, ValueError):
    """Cena pedida que não existe ou que ainda não tem fala."""


def _takes(voice_dir: Path, scene_id: str, provider: str) -> list[Path]:
    """O WAV bruto da cena nesta voz e as cópias dele, que começam com o nome do bruto."""
    raw = sorted(voice_dir.glob(f"{scene_id}-{provider}-*.wav"))
    copies = [
        copy
        for sub in Constants.COPY_DIRS
        for wav in raw
        for copy in sorted((voice_dir / sub).glob(f"{wav.stem}-*"))
    ]
    return raw + copies


def set_aside(
    voice_dir: Path, scene_ids: Sequence[str], known: Sequence[str], provider: str, now: datetime
) -> list[Path]:
    """Move a fala atual de cada cena, na voz `provider` (a identidade do TTS), para
    `voice/tomadas-recusadas/<data>/`; devolve os destinos. As falas de outras vozes ficam."""
    unknown = [scene_id for scene_id in scene_ids if scene_id not in known]
    if unknown:
        raise RetakeError(f"cena(s) fora do roteiro: {', '.join(unknown)}")
    found = {scene_id: _takes(voice_dir, scene_id, provider) for scene_id in scene_ids}
    empty = [scene_id for scene_id, takes in found.items() if not takes]
    if empty:
        raise RetakeError(f"cena(s) sem fala para refazer: {', '.join(empty)}")
    target = voice_dir / Constants.REJECTED_DIR / now.strftime(Constants.STAMP)
    moved = []
    for takes in found.values():
        for take in takes:
            destination = target / take.relative_to(voice_dir)
            destination.parent.mkdir(parents=True, exist_ok=True)
            take.replace(destination)
            moved.append(destination)
    return moved
