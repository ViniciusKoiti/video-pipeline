"""Perfil de formato do nicho (`formato_brief.v1`, ADR 031 parte B) a partir da análise já feita.

Uso: python3 -I brief.py <pasta>/analise --nicho "Nome do nicho" [--data AAAA-MM-DD]

Lê `tercos.csv` e `correlacoes.csv` (de `analisar.py`) e grava `formato-brief-<grupo>.json` na mesma pasta,
um por grupo. Cada medida leva a mediana do terço de mais views (`alto`) e do de menos (`baixo`), o `n`, o ρ
de Spearman com log(views) e a força:
- `pattern`: n >= 20, |ρ| >= 0,4 e o terço de cima diferente do de baixo na mesma direção do ρ (decisão D5 da
  spec `docs/specs/outline-numeros.md`);
- `hint`: o resto.

Só entram as medidas que o roteiro também calcula (`vp numeros`). O perfil é forma, nunca fonte (§2.2). Para
levar ao episódio: `scripts/provisorio/formato_resumo.py <episódio> <formato-brief-<grupo>.json>`. Só usa a
biblioteca padrão.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

MEASURES = (
    "duracao_s",
    "palavras_min",
    "cortes_min",
    "plano_medio_s",
    "voce_por_mil",
    "nos_por_mil",
    "eu_por_mil",
    "fonte_por_mil",
    "palavras_60s",
    "voce_60s",
    "cortes_60s",
)
MIN_N = 20
MIN_RHO = 0.4


def strength(high: float, low: float, rho: float | None, n: int) -> str:
    if rho is None or n < MIN_N or abs(rho) < MIN_RHO:
        return "hint"
    return "pattern" if (high - low) * rho > 0 else "hint"


def _float(text: str) -> float | None:
    try:
        return float(text)
    except ValueError:
        return None


def build(folder: Path, niche: str, day: date) -> dict[str, dict]:
    with (folder / "tercos.csv").open(encoding="utf-8", newline="") as handle:
        thirds = list(csv.DictReader(handle))
    with (folder / "correlacoes.csv").open(encoding="utf-8", newline="") as handle:
        corr = {(row["grupo"], row["medida"]): row for row in csv.DictReader(handle)}
    briefs: dict[str, dict] = {}
    for group in sorted({row["grupo"] for row in thirds}):
        rows = {row["terco"]: row for row in thirds if row["grupo"] == group}
        if not {"alto", "baixo"} <= rows.keys():
            continue
        measures = {}
        for name in MEASURES:
            high, low = _float(rows["alto"].get(name, "")), _float(rows["baixo"].get(name, ""))
            if high is None or low is None:
                continue
            row = corr.get((group, name), {})
            n, rho = int(row.get("n") or 0), _float(row.get("rho_log_views", ""))
            force = strength(high, low, rho, n)
            measures[name] = {"alto": high, "baixo": low, "rho": rho, "n": n, "forca": force}
        sizes = [int(row["n"]) for (g, _), row in corr.items() if g == group and row.get("n")]
        briefs[group] = {
            "schema": "formato_brief.v1",
            "nicho": niche,
            "grupo": group,
            "data": day.isoformat(),
            "n": max(sizes, default=0),
            "medidas": measures,
        }
    return briefs


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("analise", help="a pasta analise/ de analisar.py")
    parser.add_argument("--nicho", required=True)
    parser.add_argument("--data", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    folder = Path(args.analise)
    for group, brief in build(folder, args.nicho, args.data).items():
        out = folder / f"formato-brief-{group}.json"
        out.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        patterns = [name for name, m in brief["medidas"].items() if m["forca"] == "pattern"]
        print(f"{out}: {len(brief['medidas'])} medidas, pattern: {', '.join(patterns) or 'nenhuma'}")


if __name__ == "__main__":
    main()
