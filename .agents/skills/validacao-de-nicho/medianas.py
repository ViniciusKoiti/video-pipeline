"""Refaz as medianas por grupo de formato a partir do CSV da medição de demanda.

Uso: python3 -I medianas.py <csv> [idade_min_dias] [idade_max_dias]

Por canal: mediana de views dos vídeos com idade entre os limites (padrão 14 a 180 dias).
Por grupo: número de canais e mediana, p25 e p90 das medianas dos canais.
"""

import csv
import statistics
import sys
from collections import defaultdict


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    return statistics.quantiles(ordered, n=100, method="inclusive")[round(q * 100) - 1]


def main() -> None:
    path = sys.argv[1]
    low = float(sys.argv[2]) if len(sys.argv) > 2 else 14
    high = float(sys.argv[3]) if len(sys.argv) > 3 else 180
    per_channel: dict[tuple[str, str], list[int]] = defaultdict(list)
    with open(path, encoding="utf-8") as source:
        for row in csv.DictReader(source):
            try:
                age = float(row["idade_dias_aprox"])
                views = int(float(row["views"]))
            except (KeyError, ValueError):
                continue
            if low <= age <= high:
                per_channel[(row["grupo"], row["canal"])].append(views)
    groups: dict[str, list[float]] = defaultdict(list)
    for (group, _channel), views in per_channel.items():
        groups[group].append(statistics.median(views))
    print(f"vídeos com {low:g} a {high:g} dias")
    print("grupo | canais | mediana | p25 | p90")
    for group, medians in sorted(groups.items()):
        print(
            f"{group} | {len(medians)} | {statistics.median(medians):,.0f} | "
            f"{quantile(medians, 0.25):,.0f} | {quantile(medians, 0.90):,.0f}"
        )


if __name__ == "__main__":
    main()
