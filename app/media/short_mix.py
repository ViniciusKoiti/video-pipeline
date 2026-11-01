"""A mixagem de áudio de um Short (RF7; era `mix_filter` e o `ffmpeg` de `cmd_juntar` em `shorts_tec.py`).

`mix_filter` monta o filtro do ffmpeg; `has_audio` diz se o render do kit já traz som; `mix_audio` roda o
ffmpeg e, se ele falhar, levanta `MixError` em vez de deixar o traceback do `subprocess`.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from app.errors import PipelineError
from app.media.constants.loudness_constants import LoudnessConstants


class MixError(PipelineError, RuntimeError):
    pass


def mix_filter(
    starts_ms: list[int],
    video_sec: float,
    target_lufs: float = LoudnessConstants.TARGET_LUFS,
    trims: list[tuple[float, float]] | None = None,
    video_audio: bool = False,
    effects: list[tuple[int, float, float]] | None = None,
) -> str:
    """O filtro do ffmpeg: cada fala (entradas 1..N) cortada no trecho falado, reamostrada, atrasada até o
    começo da cena dela, somadas sem normalizar (com o áudio que o render já traz, se `video_audio`, e com os
    efeitos, entradas N+1.., cada um `(início em ms, corte do começo em s, ganho em dB)`), com silêncio até o
    fim do vídeo, em estéreo antes do loudnorm (o mesmo canal nos dois lados: um Short mono medido num canal
    só saía 3 dB acima do alvo tocado nos dois alto-falantes, como o YouTube mede; emenda da ADR 035), o
    volume no alvo e 48 kHz (o loudnorm sobe a taxa de amostragem; sem o aresample o AAC sai em 96 kHz)."""
    parts = []
    if video_audio:
        parts.append("[0:a]aformat=sample_rates=48000:channel_layouts=mono[v0a]")
    for i, ms in enumerate(starts_ms):
        trim = f"atrim={trims[i][0]:.3f}:{trims[i][1]:.3f},asetpts=PTS-STARTPTS," if trims else ""
        parts.append(
            f"[{i + 1}:a]{trim}aformat=sample_rates=48000:channel_layouts=mono,adelay={ms}|{ms}[v{i}]"
        )
    for j, (ms, trim_s, gain_db) in enumerate(effects or []):
        trim = f"atrim=start={trim_s:.3f},asetpts=PTS-STARTPTS," if trim_s > 0 else ""
        parts.append(
            f"[{len(starts_ms) + 1 + j}:a]{trim}aformat=sample_rates=48000:channel_layouts=mono,"
            f"volume={gain_db:.1f}dB,adelay={ms}|{ms}[e{j}]"
        )
    inputs = (
        ("[v0a]" if video_audio else "")
        + "".join(f"[v{i}]" for i in range(len(starts_ms)))
        + "".join(f"[e{j}]" for j in range(len(effects or [])))
    )
    count = len(starts_ms) + (1 if video_audio else 0) + len(effects or [])
    parts.append(
        f"{inputs}amix=inputs={count}:normalize=0:dropout_transition=0,apad=whole_dur={video_sec:.3f},"
        f"aformat=channel_layouts=stereo,loudnorm=I={target_lufs:.0f}:TP=-1.5:LRA=11,aresample=48000[voz]"
    )
    return ";".join(parts)


def has_audio(video: Path) -> bool:
    """O MP4 tem faixa de áudio (um render com som dentro, como um vídeo tocando na montagem)."""
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            str(video),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return "audio" in probe.stdout


def mix_audio(command: list[str]) -> None:
    """Roda o ffmpeg da junção; falha vira `MixError` com o fim da mensagem dele."""
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise MixError(f"ffmpeg falhou na junção: {result.stderr.strip()[-300:]}")
