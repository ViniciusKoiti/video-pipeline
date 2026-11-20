"""Os dados de uma montagem em TSX com o kit (RF7; eram `cmd_boca` de `shorts_tec.py`): as batidas (cena,
quadro inicial, duração, trecho da fala) e o envelope da boca por quadro do vídeo inteiro
(`app/media/envelope.py`, o mesmo do apresentador do auto-play)."""

from __future__ import annotations

from typing import Any

from app.media.envelope import mouth_levels
from app.pipeline.models.motion_content import MotionContent
from app.pipeline.models.voiced_speech import VoicedSpeech


def mouth_data(content: MotionContent, wavs: dict[str, VoicedSpeech]) -> dict[str, Any]:
    """`{"fps", "beats", "levels", "recordings"}`; o manifesto da pele e o texto da tela, se houver, são
    acrescentados por quem chama."""
    fps = content.fps
    starts = content.starts()
    total = sum(round(float(s["durationSec"]) * fps) for s in content.raw["scenes"])
    levels = [0.0] * total
    beats = []
    for scene in content.raw["scenes"]:
        start = round(starts[scene["id"]] * fps)
        duration = round(float(scene["durationSec"]) * fps)
        beat: dict[str, Any] = {"id": scene["id"], "from": start, "duration": duration}
        speech = wavs.get(scene["id"])
        if speech:
            begin, end = round(speech.begin * fps), round(speech.end * fps)
            for i, level in enumerate(mouth_levels(speech.wav, fps, end)[begin:end]):
                if start + i < total:
                    levels[start + i] = level
            beat["speech"] = [0, end - begin]
        beats.append(beat)
    return {"fps": fps, "beats": beats, "levels": levels, "recordings": {}}
