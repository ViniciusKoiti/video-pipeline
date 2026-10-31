"""Recusa arquivos grandes no commit: o GitHub rejeita o push acima de 100 MB e o estrago fica no histórico.

Uso: `python scripts/check_tamanho.py [--limite-mb=50]`; confere o que está no índice (`git add`).
"""

from __future__ import annotations

import subprocess
import sys

LIMITE_MB = 50


def staged_sizes() -> list[tuple[int, str]]:
    names = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=AM", "-z"],
        capture_output=True, text=True, check=True,
    ).stdout.split("\0")
    sizes = []
    for name in filter(None, names):
        size = subprocess.run(
            ["git", "cat-file", "-s", f":{name}"], capture_output=True, text=True, check=True
        ).stdout.strip()
        sizes.append((int(size), name))
    return sizes


def main(argv: list[str]) -> int:
    limit_mb = next((float(a.split("=", 1)[1]) for a in argv if a.startswith("--limite-mb=")), LIMITE_MB)
    big = [(size, name) for size, name in staged_sizes() if size > limit_mb * 1024 * 1024]
    for size, name in sorted(big, reverse=True):
        print(
            f"commit recusado: {name} tem {size / 1024 / 1024:.0f} MB (limite {limit_mb:.0f} MB)",
            file=sys.stderr,
        )
    if big:
        print("Tire do índice (`git rm --cached`) e ponha a pasta no .gitignore.", file=sys.stderr)
    return 1 if big else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
