"""Folhas de contato dos candidatos: uma por pedido, com as miniaturas numeradas e a duração.

Uso: python3 -I folhas.py <episódio> [--raiz .] [--pedidos t01-estadio t02-biblioteca] [--max 16]

Lê `data/episodes/<episódio>/candidatos/<pedido>.json` (gravado por `buscar_candidatos.py`) e grava, em
`candidatos/galeria/`, `<pedido>.jpg` (4 colunas, o texto do plano no alto) e `<pedido>.ids.json` (os ids na
mesma ordem dos números). Sem `--pedidos`, faz todos. Precisa de ffmpeg com drawtext e da fonte DejaVu Sans.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
COLUMNS = 4
CELL_W, CELL_H = 400, 240


def escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("'", "’").replace(":", "\\:").replace("%", "\\%")


def cell(thumb: Path, label: str, out: Path) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(thumb),
            "-frames:v",
            "1",
            "-vf",
            f"scale={CELL_W - 8}:{CELL_H - 8}:force_original_aspect_ratio=decrease,"
            f"pad={CELL_W}:{CELL_H}:(ow-iw)/2:(oh-ih)/2:color=0x111111,"
            f"drawtext=fontfile={FONT}:text='{escape(label)}':x=8:y=6:fontsize=22:fontcolor=white:"
            "box=1:boxcolor=black@0.8",
            str(out),
        ],
        check=True,
    )


def sheet(root: Path, request: Path, out_dir: Path, limit: int) -> int:
    data = json.loads(request.read_text(encoding="utf-8"))
    candidates = data["candidatos"][:limit]
    if not candidates:
        return 0
    pedido = data["pedido"]
    with tempfile.TemporaryDirectory() as tmp:
        for i, cand in enumerate(candidates, 1):
            duration = cand.get("duracao_s")
            label = f"{i}  {duration:.0f}s" if duration else str(i)
            cell(root / cand["miniatura"], label, Path(tmp) / f"{i:03d}.png")
        rows = -(-len(candidates) // COLUMNS)
        title = escape(pedido.get("plano", pedido["id"])[:110])
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-i",
                f"{tmp}/%03d.png",
                "-frames:v",
                "1",
                "-vf",
                f"tile={COLUMNS}x{rows},pad=iw:ih+40:0:40:color=0x111111,"
                f"drawtext=fontfile={FONT}:text='{title}':x=8:y=8:fontsize=22:fontcolor=0xffd400",
                str(out_dir / f"{pedido['id']}.jpg"),
            ],
            check=True,
        )
    ids = [cand["ativo"]["id"] for cand in candidates]
    (out_dir / f"{pedido['id']}.ids.json").write_text(json.dumps(ids, indent=0), encoding="utf-8")
    return len(candidates)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("episodio")
    parser.add_argument("--raiz", default=".", help="raiz do repositório (padrão: a pasta atual)")
    parser.add_argument("--pedidos", nargs="*", help="ids dos pedidos (padrão: todos)")
    parser.add_argument("--max", type=int, default=16, help="miniaturas por folha (padrão: 16)")
    args = parser.parse_args()

    root = Path(args.raiz).resolve()
    folder = root / "data" / "episodes" / args.episodio / "candidatos"
    out_dir = folder / "galeria"
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = set(args.pedidos or [])
    for request in sorted(folder.glob("*.json")):
        if wanted and request.stem not in wanted:
            continue
        print(f"{request.stem}: {sheet(root, request, out_dir, args.max)} candidatos")


if __name__ == "__main__":
    main()
