"""Driver do experimento MoneyPrinterTurbo (etapa 8). Roda no Python do MPT, com cwd na raiz dele.

Usa só funções do próprio MPT: `render_image_zoom_video` (imagem → clipe com zoom de 3%/s),
`combine_videos` (modo sequential, ajuste ao quadro) e `generate_video` (legendas e codificação).
Nossa única intervenção: um clipe por cena com a duração exata da voz, na ordem, sem música de fundo
(a aleatória do MPT não tem licença registrada, §9).

Uso: python mpt_driver.py pedido.json
"""

import json
import math
import shutil
import sys
from pathlib import Path

from app.models.schema import VideoAspect, VideoConcatMode, VideoFitMode, VideoParams
from app.services import video
from pydub import AudioSegment


def slot_seconds(scenes: list[dict], i: int) -> float:
    last = scenes[i]["start_ms"] + scenes[i]["duration_ms"]
    end = scenes[i + 1]["start_ms"] if i + 1 < len(scenes) else last
    return (end - scenes[i]["start_ms"]) / 1000


def main(request_path: str) -> None:
    request = json.loads(Path(request_path).read_text())
    episode, episode_dir = request["episode"], Path(request["episode_dir"])
    work = Path(request["work_dir"])
    work.mkdir(parents=True, exist_ok=True)
    scenes = episode["scenes"]

    clips = []
    for i, scene in enumerate(scenes):
        image = work / f"{scene['id']}{Path(scene['image']).suffix}"
        shutil.copyfile(episode_dir / scene["image"], image)  # o MPT grava o clipe ao lado da imagem
        clips.append(video.render_image_zoom_video(str(image), slot_seconds(scenes, i)))

    narration = AudioSegment.silent(duration=scenes[0]["start_ms"])
    cursor = scenes[0]["start_ms"]
    for scene in scenes:
        narration += AudioSegment.silent(duration=max(scene["start_ms"] - cursor, 0))
        narration += AudioSegment.from_wav(episode_dir / scene["audio"])
        cursor = scene["start_ms"] + scene["duration_ms"]
    audio = work / "narration.wav"
    narration.export(audio, format="wav")

    combined = work / "combined.mp4"
    video.combine_videos(
        str(combined),
        clips,
        str(audio),
        video_aspect=VideoAspect.landscape,
        video_concat_mode=VideoConcatMode.sequential,
        video_transition_mode=None,
        max_clip_duration=math.ceil(max(slot_seconds(scenes, i) for i in range(len(scenes)))) + 1,
        threads=request["threads"],
        video_fit_mode=VideoFitMode(request["fit_mode"]),
    )
    params = VideoParams(
        video_subject=episode["title"],
        video_aspect=VideoAspect.landscape,
        subtitle_enabled=request["subtitles"],
        font_name=request["font"],
        bgm_type="",
        n_threads=request["threads"],
    )
    captions = episode.get("captions")
    subtitle = str(episode_dir / captions) if request["subtitles"] and captions else ""
    video.generate_video(str(combined), str(audio), subtitle, request["out"], params)


if __name__ == "__main__":
    main(sys.argv[1])
