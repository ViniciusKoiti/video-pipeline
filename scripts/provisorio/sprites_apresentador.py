"""Sprites do apresentador a partir de uma folha gerada (provisório, ADR 017 em proposta).

Uso: `.venv/bin/python scripts/provisorio/sprites_apresentador.py <comando> ...`

  cortar <folha.png> <pasta>     corta a folha 6×2 em `l<linha>c<coluna>.png`, todas do mesmo tamanho
  medir <pasta>                  encaixa cada célula na `l1c1`; mostra o deslocamento e a diferença que sobra
  montar <pasta> <saída>         camadas com fundo transparente: `base.png`, `boca-<visema>.png`,
                                 `olhos-fechados.png` e, para conferência, os 12 quadros em `quadros/`

- A folha: fundo verde chapado (#00FF00), 6 colunas separadas por uma calha verde, na ordem dos visemas do
  kit (`rest`, `mbp`, `ei`, `a`, `ou`, `fv`); linha 1 de olho aberto, linha 2 de olho fechado. O busto vai até
  o pé da célula, e é por ele que a linha 2 é achada.
- A cabeça fica parada por construção: a `l1c1` é a base, e das outras células só entra a região da boca (ou
  dos olhos), depois de encaixada na base por deslocamento. Por isso a folha precisa vir com a cabeça de
  frente em todas as células; giro e inclinação o encaixe não corrige.
- As regiões são frações da célula, medidas na folha de 2026-10-12; outro enquadramento pede outros números.
- Nenhum comando sobrescreve: a pasta de saída tem de ser nova.
- Folhas e sprites com a aparência do dono são dado pessoal: ficam fora do Git.
- Usa numpy, que vem com o extra `tts`, e o ffmpeg para ler e gravar PNG.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

Image = np.ndarray[Any, np.dtype[np.float64]]
Box = tuple[float, float, float, float]

VISEMES = ("rest", "mbp", "ei", "a", "ou", "fv")
ROWS = 2

# Elipses (centro x, centro y, raio x, raio y), em fração da largura e da altura da célula.
MOUTH: Box = (0.528, 0.493, 0.131, 0.060)
EYES: Box = (0.525, 0.329, 0.184, 0.031)
# Âncoras do encaixe (y0, y1, x0, x1), em fração: nariz e maçãs do rosto não mudam com a boca; as
# sobrancelhas não mudam com a piscada.
NOSE: Box = (0.309, 0.430, 0.367, 0.682)
BROW: Box = (0.242, 0.295, 0.328, 0.721)
FEATHER = 0.016  # borda suave das elipses, em fração da largura
REACH = 0.052  # até onde o encaixe procura, em fração da largura
DIFFERENT = 90  # soma das diferenças dos três canais acima da qual um pixel conta como diferente


def read_png(path: Path) -> Image:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )  # fmt: skip
    width, height = (int(v) for v in probe.stdout.strip().split(","))
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True,
    )  # fmt: skip
    return np.frombuffer(raw.stdout, np.uint8).reshape(height, width, 3).astype(np.float64)


def write_png(image: Image, path: Path) -> None:
    """Grava RGB ou RGBA; `-n` faz o ffmpeg recusar um arquivo que já existe."""
    height, width, channels = image.shape
    data = np.clip(image.round(), 0, 255).astype(np.uint8).tobytes()
    subprocess.run(
        ["ffmpeg", "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgba" if channels == 4 else "rgb24",
         "-s", f"{width}x{height}", "-i", "-", "-frames:v", "1", str(path)],
        input=data, check=True,
    )  # fmt: skip


def green_mask(image: Image) -> np.ndarray[Any, np.dtype[np.bool_]]:
    r, g, b = image[..., 0], image[..., 1], image[..., 2]
    return (g > 200) & (r < 90) & (b < 90)


def runs(mask: list[bool]) -> list[tuple[int, int]]:
    """Trechos seguidos de `True`, como (início, fim exclusivo)."""
    found: list[tuple[int, int]] = []
    start: int | None = None
    for i, value in enumerate([*mask, False]):
        if value and start is None:
            start = i
        if not value and start is not None:
            found.append((start, i))
            start = None
    return found


def split_sheet(sheet: Image) -> dict[tuple[int, int], Image]:
    """Células por (linha, coluna), a partir de 1, aparadas para o mesmo tamanho.

    As colunas saem das calhas verdes; a linha 2 começa onde o busto da linha 1 dá lugar ao verde. Na
    largura a sobra é aparada dos dois lados; na altura, de cima, porque o busto se apoia no pé da célula.
    """
    height, width, _ = sheet.shape
    green = green_mask(sheet)
    gutters = [r for r in runs(list(green.mean(axis=0) > 0.97)) if r[1] - r[0] >= 3]
    starts = [0, *(end for _, end in gutters)]
    ends = [*(start for start, _ in gutters), width]
    cols = [(s, e) for s, e in zip(starts, ends, strict=True) if e - s > width / 20]
    if len(cols) != len(VISEMES):
        raise ValueError(f"esperava {len(VISEMES)} colunas separadas por calha verde, achei {len(cols)}")
    by_row = green.mean(axis=1)
    middle, span = height // 2, height // 10
    candidates = range(middle - span, middle + span)
    cut = next((y for y in candidates if by_row[y - 1] < 0.2 and by_row[y] > 0.5), None)
    if cut is None:
        raise ValueError("não achei onde a linha de baixo começa (busto da linha 1 seguido de verde)")
    raw = {
        (r, c): sheet[y0:y1, x0:x1]
        for r, (y0, y1) in enumerate([(0, cut), (cut, height)], 1)
        for c, (x0, x1) in enumerate(cols, 1)
    }
    w = min(cell.shape[1] for cell in raw.values())
    h = min(cell.shape[0] for cell in raw.values())
    cells: dict[tuple[int, int], Image] = {}
    for position, cell in raw.items():
        dx = (cell.shape[1] - w) // 2
        cells[position] = np.ascontiguousarray(cell[cell.shape[0] - h :, dx : dx + w])
    return cells


def pixels(box: Box, shape: tuple[int, ...]) -> tuple[int, int, int, int]:
    """Uma âncora (y0, y1, x0, x1) em fração, em pixels da célula."""
    height, width = shape[0], shape[1]
    return round(box[0] * height), round(box[1] * height), round(box[2] * width), round(box[3] * width)


def shift(image: Image, dx: int, dy: int) -> Image:
    return np.roll(np.roll(image, dy, axis=0), dx, axis=1)


def fit(image: Image, ref: Image, anchor: Box) -> tuple[int, int]:
    """Deslocamento inteiro (dx, dy) que melhor encaixa `image` em `ref` dentro da âncora."""
    y0, y1, x0, x1 = pixels(anchor, ref.shape)
    reach = max(1, round(REACH * ref.shape[1]))
    target = ref[y0:y1, x0:x1]
    best: tuple[float, int, int] | None = None
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            error = float(np.abs(image[y0 - dy : y1 - dy, x0 - dx : x1 - dx] - target).mean())
            if best is None or error < best[0]:
                best = (error, dx, dy)
    assert best is not None
    return best[1], best[2]


def ellipse(shape: tuple[int, ...], region: Box) -> Image:
    """Máscara de 0 a 1: 1 dentro da elipse, 0 fora, com uma rampa de `FEATHER` na borda."""
    height, width = shape[0], shape[1]
    cx, cy, rx, ry = region[0] * width, region[1] * height, region[2] * width, region[3] * height
    yy, xx = np.mgrid[:height, :width]
    distance = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    return np.clip((1 - distance) * min(rx, ry) / (FEATHER * width) + 0.5, 0, 1)


def key(image: Image) -> Image:
    """Tira o fundo verde: o alfa sai da sobra de verde sobre os outros canais; o que vazou é aparado."""
    r, g, b = image[..., 0], image[..., 1], image[..., 2]
    other = np.maximum(r, b)
    alpha = np.clip(1 - (g - other - 40) / 110, 0, 1)
    out = image.copy()
    out[..., 1] = np.minimum(g, other + 8)
    return np.dstack([out, alpha * 255])


def blend(under: Image, over: Image, mask: Image) -> Image:
    return under * (1 - mask[..., None]) + over * mask[..., None]


def load_cells(folder: Path) -> dict[tuple[int, int], Image]:
    return {
        (r, c): read_png(folder / f"l{r}c{c}.png")
        for r in range(1, ROWS + 1)
        for c in range(1, len(VISEMES) + 1)
    }


def new_folder(path: Path) -> Path:
    if path.exists():
        sys.exit(f"{path} já existe; escolha uma pasta nova (este script não sobrescreve)")
    path.mkdir(parents=True)
    return path


def cmd_cortar(args: argparse.Namespace) -> None:
    cells = split_sheet(read_png(args.folha))
    out = new_folder(args.pasta)
    for (r, c), cell in cells.items():
        write_png(cell, out / f"l{r}c{c}.png")
    height, width, _ = next(iter(cells.values())).shape
    print(f"{len(cells)} células de {width}×{height} px em {out}")


def cmd_medir(args: argparse.Namespace) -> None:
    cells = load_cells(args.pasta)
    ref = cells[1, 1]
    still = (1 - ellipse(ref.shape, MOUTH)) * (1 - ellipse(ref.shape, EYES)) > 0.5
    print("célula  dx  dy  diferente fora da boca e dos olhos")
    for (r, c), cell in cells.items():
        dx, dy = fit(cell, ref, NOSE if r == 1 else BROW)
        different = np.abs(shift(cell, dx, dy) - ref).sum(axis=2) > DIFFERENT
        print(f"l{r}c{c}   {dx:+3d} {dy:+3d}  {100 * float(different[still].mean()):5.1f}%")


def cmd_montar(args: argparse.Namespace) -> None:
    cells = load_cells(args.pasta)
    ref = cells[1, 1]
    out = new_folder(args.saida)
    frames = new_folder(out / "quadros")
    mouth, eyes = ellipse(ref.shape, MOUTH), ellipse(ref.shape, EYES)
    write_png(key(ref), out / "base.png")
    mouths: dict[str, Image] = {}
    for c, viseme in enumerate(VISEMES, 1):
        dx, dy = fit(cells[1, c], ref, NOSE)
        mouths[viseme] = shift(cells[1, c], dx, dy)
        write_png(np.dstack([mouths[viseme], mouth * 255]), out / f"boca-{viseme}.png")
        print(f"boca {viseme:4} encaixe dx={dx:+d} dy={dy:+d}")
    dx, dy = fit(cells[2, 1], ref, BROW)
    closed = shift(cells[2, 1], dx, dy)
    write_png(np.dstack([closed, eyes * 255]), out / "olhos-fechados.png")
    print(f"olhos fechados encaixe dx={dx:+d} dy={dy:+d}")
    for viseme in VISEMES:
        frame = blend(ref, mouths[viseme], mouth)
        write_png(key(frame), frames / f"{viseme}.png")
        write_png(key(blend(frame, closed, eyes)), frames / f"{viseme}-piscada.png")
    print(f"camadas em {out}, quadros de conferência em {frames}")


def main() -> None:
    raw = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=raw)
    sub = parser.add_subparsers(dest="comando", required=True)
    cortar = sub.add_parser("cortar")
    cortar.add_argument("folha", type=Path)
    cortar.add_argument("pasta", type=Path)
    cortar.set_defaults(run=cmd_cortar)
    medir = sub.add_parser("medir")
    medir.add_argument("pasta", type=Path)
    medir.set_defaults(run=cmd_medir)
    montar = sub.add_parser("montar")
    montar.add_argument("pasta", type=Path)
    montar.add_argument("saida", type=Path)
    montar.set_defaults(run=cmd_montar)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
