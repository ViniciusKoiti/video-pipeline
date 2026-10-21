"""Escolhe a amostra de vídeos a analisar a partir do CSV da medição de demanda.

Uso:
  python3 -I amostra.py <csv> <saida.tsv> [--grupos H H0] [--por-grupo 4] [--max-por-canal 1]
                        [--min-duracao 180] [--incluir ID ...]

- Lê o CSV de `validacao-de-nicho/coleta.py` (colunas canal, grupo, video_id, titulo, duracao_s, views...).
- Por grupo, ordena por views e pega os primeiros, no máximo `--max-por-canal` vídeos de cada canal, só vídeos
  com pelo menos `--min-duracao` segundos (corta Shorts).
- `--incluir` acrescenta vídeos escolhidos pelo dono (por exemplo, o concorrente direto do tema), marcados
  como
  `incluido`.
- Mesmo CSV e mesmos parâmetros dão sempre a mesma amostra. A saída é um TSV: video_id, grupo, canal, views,
  duracao_s, motivo, titulo.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("csv")
    parser.add_argument("saida")
    parser.add_argument("--grupos", nargs="+", default=["H", "H0"])
    parser.add_argument("--por-grupo", type=int, default=4)
    parser.add_argument("--max-por-canal", type=int, default=1)
    parser.add_argument("--min-duracao", type=int, default=180)
    parser.add_argument("--incluir", nargs="*", default=[])
    args = parser.parse_args()

    best: dict[str, dict[str, str]] = {}
    with Path(args.csv).open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if not row.get("views", "").isdigit():
            continue
        current = best.get(row["video_id"])
        if current is None or int(row["views"]) > int(current["views"]):
            best[row["video_id"]] = row
    rows = sorted(best.values(), key=lambda r: (-int(r["views"]), r["video_id"]))

    chosen: list[tuple[dict[str, str], str]] = []
    for group in args.grupos:
        per_channel: dict[str, int] = {}
        taken = 0
        for row in rows:
            if taken >= args.por_grupo:
                break
            duration = int(row["duracao_s"]) if row.get("duracao_s", "").isdigit() else 0
            if row["grupo"] != group or duration < args.min_duracao:
                continue
            if per_channel.get(row["canal"], 0) >= args.max_por_canal:
                continue
            per_channel[row["canal"]] = per_channel.get(row["canal"], 0) + 1
            taken += 1
            chosen.append((row, f"top {taken} do grupo {group}"))
    picked = {row["video_id"] for row, _ in chosen}
    for video_id in args.incluir:
        if video_id in picked:
            continue
        row = best.get(
            video_id,
            {"video_id": video_id, "grupo": "-", "canal": "-", "views": "", "duracao_s": "", "titulo": ""},
        )
        chosen.append((row, "incluido"))

    with Path(args.saida).open("w", encoding="utf-8") as out:
        out.write("video_id\tgrupo\tcanal\tviews\tduracao_s\tmotivo\ttitulo\n")
        for row, reason in chosen:
            fields = [
                row["video_id"],
                row["grupo"],
                row["canal"],
                row["views"],
                row["duracao_s"],
                reason,
                row["titulo"].replace("\t", " "),
            ]
            out.write("\t".join(fields) + "\n")
            print("\t".join(fields[:6]), "\t", fields[6][:70])


if __name__ == "__main__":
    main()
