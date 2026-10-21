"""Baixa, para análise, a legenda, os metadados e uma cópia em baixa resolução de cada vídeo da amostra.

Uso:
  python3 -I baixar.py <amostra.tsv> <pasta> [--cookies ARQ] [--ytdlp CAMINHO] [--altura 360] [--sem-video]
                       [--idiomas "pt-orig,pt,pt-BR"]

- `amostra.tsv`: saída de `amostra.py` (primeira coluna = video_id) ou um arquivo com um id por linha.
- `pasta`: fora do Git (padrão sugerido: `data/cache/nicho/<titulo>/`). Material de terceiros, só para
  análise.
- Por vídeo: `<id>.info.json`, `<id>.*.vtt` (legenda do autor ou automática) e `<id>.mp4` com no máximo
  `--altura` linhas. O que já existe na pasta não é baixado de novo.
- yt-dlp: `--ytdlp` ou a variável `YTDLP`; precisa de Node.js para o desafio JS do YouTube (`--js-runtimes
  node`).
- Cookies: só com autorização do dono. O arquivo é copiado para a pasta com permissão 600, usado e apagado
  no fim,
  porque o yt-dlp regrava o arquivo de cookies que recebe. O original não é tocado.
- Só as legendas originais (`--idiomas`), sem as traduções automáticas, que o YouTube limita (HTTP 429).
  Falha de
  uma legenda não impede os metadados (`--ignore-errors`).
- Pausa de 3 s entre requisições. "Sign in to confirm you're not a bot" sem cookies: para com código 4.
  HTTP 429:
  para com código 3; espere antes de rodar de novo, que o script continua de onde parou.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PAUSE_S = 3
BOT_CHECK = "Sign in to confirm"
RATE_LIMIT = "HTTP Error 429"


def ids_from(path: Path) -> list[str]:
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        first = line.split("\t", 1)[0].strip()
        if first and first != "video_id" and not first.startswith("#"):
            ids.append(first)
    return ids


def run(command: list[str], log: Path) -> str:
    time.sleep(PAUSE_S)
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    with log.open("a", encoding="utf-8") as out:
        out.write(" ".join(c if "cookies" not in c else "<cookies>" for c in command) + "\n")
        out.write(result.stdout[-2000:] + result.stderr[-2000:] + "\n")
    return result.stdout + result.stderr


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("amostra")
    parser.add_argument("pasta")
    parser.add_argument("--cookies")
    parser.add_argument("--ytdlp", default=os.environ.get("YTDLP", "yt-dlp"))
    parser.add_argument("--altura", type=int, default=360)
    parser.add_argument("--sem-video", action="store_true")
    parser.add_argument("--idiomas", default="pt-orig,pt,pt-BR")
    args = parser.parse_args()

    folder = Path(args.pasta)
    folder.mkdir(parents=True, exist_ok=True)
    log = folder / "baixar.log"
    jar = None
    if args.cookies:
        jar = folder / ".cookies-copia.txt"
        shutil.copy(args.cookies, jar)
        jar.chmod(0o600)
    base = [args.ytdlp, "--js-runtimes", "node", "--no-progress", "--ignore-errors"]
    if jar:
        base += ["--cookies", str(jar)]
    out_template = str(folder / "%(id)s.%(ext)s")
    status = 0
    try:
        for video_id in ids_from(Path(args.amostra)):
            url = f"https://www.youtube.com/watch?v={video_id}"
            has_meta = (folder / f"{video_id}.info.json").exists() and any(folder.glob(f"{video_id}.*.vtt"))
            if not has_meta:
                output = run(
                    base
                    + [
                        "--skip-download",
                        "--write-info-json",
                        "--write-subs",
                        "--write-auto-subs",
                        "--sub-langs",
                        args.idiomas,
                        "--sub-format",
                        "vtt",
                        "-o",
                        out_template,
                        url,
                    ],
                    log,
                )
                if BOT_CHECK in output:
                    print(f"{video_id}: o YouTube pediu login; rode com --cookies (com autorização do dono)")
                    status = 4
                    break
                if RATE_LIMIT in output and not (folder / f"{video_id}.info.json").exists():
                    print(f"{video_id}: HTTP 429 do YouTube; pare, espere e rode de novo")
                    status = 3
                    break
            if not args.sem_video and not (folder / f"{video_id}.mp4").exists():
                run(
                    base
                    + [
                        "-f",
                        f"bv*[height<={args.altura}]+ba/b[height<={args.altura}]",
                        "--merge-output-format",
                        "mp4",
                        "-o",
                        out_template,
                        url,
                    ],
                    log,
                )
            got = [p.suffix for p in folder.glob(f"{video_id}.*") if p.suffix in (".json", ".vtt", ".mp4")]
            print(f"{video_id}: {' '.join(sorted(set(got))) or 'nada (ver baixar.log)'}")
    finally:
        if jar and jar.exists():
            jar.unlink()
    sys.exit(status)


if __name__ == "__main__":
    main()
