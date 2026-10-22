"""Conferência de um vídeo de banco: quadros espaçados do começo ao fim numa faixa.

Uso: python3 -I conferencia.py <video.mp4> <saida.jpg> [--quadros 8]

A miniatura do banco mostra um instante; pessoa, marca ou texto podem aparecer depois. A faixa cobre o clipe
inteiro para a conferência que vai no `usage_notes` do ativo. Precisa de ffmpeg e ffprobe.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def duration(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return float(out.strip())


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("video")
    parser.add_argument("saida")
    parser.add_argument("--quadros", type=int, default=8)
    args = parser.parse_args()

    video = Path(args.video)
    total = duration(video)
    subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vf",
            f"fps={args.quadros / total:.5f},scale=320:-2,tile={args.quadros}x1:padding=2",
            "-frames:v",
            "1",
            args.saida,
        ],
        check=True,
    )
    print(f"{video.name}: {total:.1f} s, {args.quadros} quadros -> {args.saida}")


if __name__ == "__main__":
    main()
