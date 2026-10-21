"""Decupagem: um quadro por cena (entre dois cortes), com o tempo e a fala daquele trecho.

Uso: python3 -I decupagem.py <video.mp4> <legenda .vtt/.srt ou transcrição .txt de medir.py> <saida/>
[--max-cenas 200]

Grava em `<saida>/<id>/`:
- `cenas.tsv`: cena, início, fim, duração e o que o narrador fala nela (linhas da legenda que começam ali);
- `cenas-N.jpg`: folhas de 30 quadros (6×5), o quadro do meio de cada cena, com número, início e duração.

Os cortes vêm de `<id>.cortes.txt` (cache de `medir.py`) ou são medidos aqui (mudança de cena acima de 0,3 no
ffmpeg; fusão e zoom lento não contam). A folha densa da abertura e do fecho é a de `folha_densa.py`.
Precisa de ffmpeg com drawtext.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import tempfile
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SCENE_THRESHOLD = 0.3
PER_SHEET = 30
COLUMNS = 6
MIN_SCENE_S = 0.2  # dois cortes mais próximos que isso são um só (clarão, piscada)


def duration(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def cuts(video: Path) -> list[float]:
    cache = video.with_suffix(".cortes.txt")
    if cache.exists():
        return [float(t) for t in cache.read_text().split()]
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(video),
            "-vf",
            f"select='gt(scene,{SCENE_THRESHOLD})',showinfo",
            "-an",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return [float(t) for t in re.findall(r"pts_time:([\d.]+)", result.stderr)]


def seconds(stamp: str) -> float:
    parts = stamp.replace(",", ".").split(":")
    return sum(float(p) * 60**i for i, p in enumerate(reversed(parts)))


def speech(path: Path) -> list[tuple[float, str]]:
    """Linhas faladas com o segundo de início, de uma legenda (.vtt/.srt) ou da transcrição de `medir.py`."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".txt":
        return [
            (int(m) * 60 + int(s), line) for m, s, line in re.findall(r"^\[(\d+):(\d+)\] (.*)$", text, re.M)
        ]
    lines, seen, start = [], set(), 0.0
    for raw in text.splitlines():
        cue = re.match(r"([\d:.,]+) -->", raw)
        if cue:
            start = seconds(cue.group(1))
            continue
        line = re.sub(r"<[^>]+>", "", raw).strip()
        if (
            not line
            or line.isdigit()
            or line == "WEBVTT"
            or line.startswith(("Kind:", "Language:"))
            or line in seen
        ):
            continue
        seen.add(line)
        lines.append((start, line))
    return lines


def scenes(times: list[float], total: float) -> list[tuple[float, float]]:
    bounds = [0.0]
    for t in sorted(times):
        if t - bounds[-1] >= MIN_SCENE_S:
            bounds.append(t)
    bounds.append(total)
    return list(zip(bounds, bounds[1:], strict=False))


def label(index: int, start: float, length: float) -> str:
    return f"#{index}  {int(start // 60):02d}\\:{start % 60:04.1f}  ({length:.1f} s)"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("video")
    parser.add_argument("legenda")
    parser.add_argument("saida")
    parser.add_argument("--max-cenas", type=int, default=200)
    args = parser.parse_args()

    video = Path(args.video)
    out = Path(args.saida) / video.stem
    out.mkdir(parents=True, exist_ok=True)
    total = duration(video)
    spans = scenes(cuts(video), total)[: args.max_cenas]
    lines = speech(Path(args.legenda))

    with (out / "cenas.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["cena", "inicio_s", "fim_s", "duracao_s", "fala"])
        for i, (start, end) in enumerate(spans, 1):
            said = " ".join(t for s, t in lines if start <= s < end)
            writer.writerow([i, f"{start:.1f}", f"{end:.1f}", f"{end - start:.1f}", said])

    with tempfile.TemporaryDirectory() as tmp:
        for i, (start, end) in enumerate(spans, 1):
            middle = start + (end - start) / 2
            subprocess.run(
                [
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-y",
                    "-ss",
                    f"{middle:.2f}",
                    "-i",
                    str(video),
                    "-frames:v",
                    "1",
                    "-vf",
                    f"scale=320:-2,drawtext=fontfile={FONT}:text='{label(i, start, end - start)}':x=4:y=4:"
                    "fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.7",
                    f"{tmp}/{i:04d}.png",
                ],
                check=True,
            )
        for sheet, first in enumerate(range(1, len(spans) + 1, PER_SHEET), 1):
            count = min(PER_SHEET, len(spans) - first + 1)
            rows = -(-count // COLUMNS)
            subprocess.run(
                [
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-y",
                    "-start_number",
                    str(first),
                    "-i",
                    f"{tmp}/%04d.png",
                    "-frames:v",
                    "1",
                    "-vf",
                    f"tile={COLUMNS}x{rows}:padding=4",
                    str(out / f"cenas-{sheet}.jpg"),
                ],
                check=True,
            )
    print(f"{video.stem}: {len(spans)} cenas em {total / 60:.1f} min -> {out}")


if __name__ == "__main__":
    main()
