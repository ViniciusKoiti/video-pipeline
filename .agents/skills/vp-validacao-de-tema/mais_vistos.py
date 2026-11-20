"""Lista os vídeos mais vistos de um canal a partir da listagem pública do yt-dlp.

Uso:
  python3 -I mais_vistos.py <canal.json> [--titulos <canal.pt.json>] [--n 15] [--min-s 300]

- <canal.json>: saída de `yt-dlp -J --flat-playlist <url do canal>/videos` (leitura padrão). As views vêm
  certas; o título pode vir traduzido para o inglês.
- --titulos: a mesma listagem lida com `--extractor-args "youtube:lang=pt"`. Só os títulos dela entram: com
  `lang=pt` o yt-dlp lê "312 mil" como 312. Sem a opção, o script procura `<canal>.pt.json` ao lado.
- --n: quantos vídeos listar (padrão 15). --min-s: duração mínima, em segundos (padrão 300).

Saída: um cabeçalho com inscritos, vídeos contados, vídeos sem contagem de views (ficam fora) e a mediana de
views dos contados (em número par, o maior dos dois valores centrais); depois, uma linha por vídeo com views,
vezes a mediana, duração, id e título. São números da data da coleta, arredondados pelo YouTube: estimativa de
interesse associado, e os mais vistos são os sobreviventes do canal.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def titles(data: dict) -> dict[str, str]:
    return {e["id"]: e["title"] for e in data.get("entries") or [] if e and e.get("id") and e.get("title")}


def rank(data: dict, pt_titles: dict[str, str], n: int = 15, min_s: int = 300) -> dict:
    """Vídeos com a duração mínima, do mais visto ao menos visto, e a mediana de views deles."""
    long_enough = [e for e in data.get("entries") or [] if e and (e.get("duration") or 0) >= min_s]
    counted = [e for e in long_enough if e.get("view_count") is not None]
    median = statistics.median_high([e["view_count"] for e in counted]) if counted else 0
    rows = [
        {
            "views": e["view_count"],
            "vezes": round(e["view_count"] / median, 1) if median else None,
            "duracao_s": int(e["duration"]),
            "id": e.get("id"),
            "titulo": pt_titles.get(e.get("id")) or e.get("title") or "",
        }
        for e in sorted(counted, key=lambda e: e["view_count"], reverse=True)[:n]
    ]
    return {
        "canal": data.get("channel") or data.get("title") or "",
        "inscritos": data.get("channel_follower_count"),
        "videos": len(counted),
        "sem_views": len(long_enough) - len(counted),
        "mediana": median,
        "min_s": min_s,
        "linhas": rows,
    }


def render(result: dict) -> list[str]:
    header = (
        f"# {result['canal']} | inscritos={result['inscritos']} | videos={result['videos']} "
        f"| sem_views={result['sem_views']} | mediana_views={result['mediana']} | min_s={result['min_s']}"
    )
    lines = [header]
    for row in result["linhas"]:
        times = "-" if row["vezes"] is None else f"{row['vezes']:.1f}x"
        duration = f"{row['duracao_s'] // 60}:{row['duracao_s'] % 60:02d}"
        lines.append(f"{row['views']:>10} | {times:>7} | {duration:>6} | {row['id']} | {row['titulo']}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("listagem", type=Path, help="JSON do yt-dlp (leitura padrão)")
    parser.add_argument("--titulos", type=Path, help="JSON da leitura com lang=pt (só os títulos entram)")
    parser.add_argument("--n", type=int, default=15)
    parser.add_argument("--min-s", type=int, default=300)
    args = parser.parse_args(argv)
    beside = args.listagem.with_suffix(".pt.json")
    pt_path = args.titulos or (beside if beside.exists() else None)
    pt_titles = titles(load(pt_path)) if pt_path else {}
    result = rank(load(args.listagem), pt_titles, args.n, args.min_s)
    if not result["videos"]:
        print(f"nenhum vídeo com views em {args.listagem}: a URL lida é a da aba /videos?", file=sys.stderr)
        return 2
    print("\n".join(render(result)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
