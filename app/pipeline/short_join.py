"""A junção da voz (e dos efeitos) sobre o MP4 silencioso de um Short (RF7; era `cmd_juntar` de
`shorts_tec.py`): quais falas entram, onde cada uma começa e o comando do ffmpeg."""

from __future__ import annotations

from pathlib import Path

from app.media.short_mix import mix_filter
from app.pipeline.constants.short_constants import ShortConstants
from app.pipeline.models.motion_content import MotionContent
from app.pipeline.models.placed_sfx import PlacedSfx
from app.pipeline.models.voiced_speech import VoicedSpeech
from app.pipeline.short_timing import ShortAssemblyError


def ordered_speech(content: MotionContent, wavs: dict[str, VoicedSpeech]) -> list[str]:
    """As cenas com fala, na ordem do vídeo. Fala de cena que não existe, ou que passa do fim da cena, é erro:
    `tempos` e um novo render resolvem."""
    starts = content.starts()
    missing = sorted(set(wavs) - set(starts))
    if missing:
        raise ShortAssemblyError(f"falas de cenas que não existem no JSON: {', '.join(missing)}")
    limits = {s["id"]: float(s["durationSec"]) for s in content.raw["scenes"]}
    ordered = [scene_id for scene_id in starts if scene_id in wavs]
    for scene_id in ordered:
        end = starts[scene_id] + wavs[scene_id].seconds
        if end > starts[scene_id] + limits[scene_id] + ShortConstants.OVERRUN_TOLERANCE_S:
            raise ShortAssemblyError(
                f"a fala de {scene_id} ({end - starts[scene_id]:.2f} s) passa do fim da cena: "
                "rode `tempos` e renderize de novo"
            )
    return ordered


def join_command(
    video: Path,
    out: Path,
    content: MotionContent,
    wavs: dict[str, VoicedSpeech],
    ordered: list[str],
    effects: list[PlacedSfx],
    video_sec: float,
    video_audio: bool,
) -> list[str]:
    """O ffmpeg: o vídeo copiado, as falas (começo da cena) e os efeitos mixados num AAC estéreo."""
    starts = content.starts()
    starts_ms = [round(starts[scene_id] * 1000) for scene_id in ordered]
    command = ["ffmpeg", "-y", "-v", "error", "-i", str(video)]
    for scene_id in ordered:
        command += ["-i", str(wavs[scene_id].wav)]
    for effect in effects:
        command += ["-i", str(effect.file)]
    graph = mix_filter(
        starts_ms,
        video_sec,
        trims=[(wavs[s].begin, wavs[s].end) for s in ordered],
        video_audio=video_audio,
        effects=[(round(e.start_s * 1000), e.trim_s, e.gain_db) for e in effects],
    )
    return [
        *command,
        "-filter_complex",
        graph,
        "-map",
        "0:v:0",
        "-map",
        "[voz]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(out),
    ]
