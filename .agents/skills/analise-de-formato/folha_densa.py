"""Folha densa: um quadro a cada 0,1 s, com o tempo escrito, para ver como o texto entra e onde o vídeo corta.

Uso: python3 -I folha_densa.py <pasta> [--posicoes 0 0.5] [--segundos 4] [--passo 0.1]

Para cada `<id>.mp4` da pasta, grava `<id>_densa_<pos>.jpg` (8 colunas) começando em `pos` × duração: a
posição 0
é a abertura; 0,5 é o meio do vídeo. A folha de 32 quadros do `medir.py` mostra o estilo; esta mostra o
movimento.
O que já existe não é refeito. Precisa de ffmpeg com drawtext e da fonte DejaVu Sans Mono.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
COLUMNS = 8


def sheet(video: Path, start: float, seconds: float, step: float, out: Path) -> None:
    frames = round(seconds / step)
    rows = -(-frames // COLUMNS)
    label = (
        f"drawtext=fontfile={FONT}:text='%{{eif\\:t+{start:.2f}\\:d}}.%{{eif\\:mod((t+{start:.2f})*10\\,10)\\:d}}'"
        ":x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.2f}",
            "-t",
            f"{seconds:.2f}",
            "-i",
            str(video),
            "-vf",
            f"fps={1 / step:.3f},scale=240:-2,{label},tile={COLUMNS}x{rows}",
            "-frames:v",
            "1",
            str(out),
        ],
        check=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("pasta")
    parser.add_argument("--posicoes", type=float, nargs="+", default=[0.0, 0.5])
    parser.add_argument("--segundos", type=float, default=4.0)
    parser.add_argument("--passo", type=float, default=0.1)
    args = parser.parse_args()

    folder = Path(args.pasta)
    for video in sorted(folder.glob("*.mp4")):
        if "." in video.stem:  # sobras do yt-dlp (`.temp.mp4`, `.f398.mp4`)
            continue
        info = folder / f"{video.stem}.info.json"
        duration = (
            float(json.loads(info.read_text(encoding="utf-8")).get("duration") or 0) if info.exists() else 0
        )
        if not duration:  # vídeo nosso, sem info.json do yt-dlp
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            duration = float(json.loads(probe)["format"]["duration"])
        for position in args.posicoes:
            out = folder / f"{video.stem}_densa_{round(position * 100):02d}.jpg"
            if out.exists():
                continue
            start = max(0.0, min(position * duration, duration - args.segundos))
            sheet(video, start, args.segundos, args.passo, out)
        print(video.stem)


if __name__ == "__main__":
    main()
