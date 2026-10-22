"""Dois moldes lado a lado: onde concordam, onde divergem (ADR 031, parte B).

Uso:
  python3 -I comparar_moldes.py <a.molde.json> <b.molde.json> [--nomes A B] [--saida comparacao.md]

Para cada medida presente nos dois, a mediana e os quartis de cada um e a leitura: `iguais` quando a mediana
de cada um cai dentro de q1–q3 do outro; senão, qual é maior. Para cada traço, a prevalência de cada um e se
concordam (os dois com metade ou mais, ou os dois com menos). O que é `padrao` nos dois é o que vale levar
para a partitura sem discussão; o que diverge é decisão do dono. É forma, nunca fato.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LIMIAR_TRACO_PCT = 50


def leitura_medida(a: dict, b: dict) -> str:
    if "q1" not in a or "q1" not in b:
        return "sem quartis"
    a_em_b = b["q1"] <= a["mediana"] <= b["q3"]
    b_em_a = a["q1"] <= b["mediana"] <= a["q3"]
    if a_em_b and b_em_a:
        return "iguais"
    if a["mediana"] > b["mediana"]:
        return "A maior"
    if a["mediana"] < b["mediana"]:
        return "B maior"
    return "iguais"


def leitura_traco(a: dict, b: dict) -> str:
    a_tem, b_tem = a["pct"] >= LIMIAR_TRACO_PCT, b["pct"] >= LIMIAR_TRACO_PCT
    if a_tem != b_tem:
        return "divergem"
    if a["forca"] == "padrao" and b["forca"] == "padrao":
        return "padrão nos dois"
    return "concordam"


def fmt(item: dict) -> str:
    if "q1" in item:
        return f"{item['mediana']:g} ({item['q1']:g}–{item['q3']:g}, n {item['n']})"
    return f"{item['mediana']:g} (n {item['n']})"


def fmt_traco(item: dict) -> str:
    return f"{item['com']}/{item['n']} ({item['pct']}%, {item['forca']})"


def comparar(a: dict, b: dict, nome_a: str, nome_b: str) -> str:
    va, vb = a.get("videos", {}), b.get("videos", {})
    linhas = [
        f"# Moldes lado a lado: {nome_a} × {nome_b}",
        "",
        f"A = {nome_a}: {va.get('n', '?')} vídeo(s), {va.get('com_batidas', 0)} com batidas, "
        f"grupos {', '.join(a.get('grupos') or []) or 'todos'}.",
        f"B = {nome_b}: {vb.get('n', '?')} vídeo(s), {vb.get('com_batidas', 0)} com batidas, "
        f"grupos {', '.join(b.get('grupos') or []) or 'todos'}.",
        "",
        "`iguais` = a mediana de cada um cai dentro de q1–q3 do outro. Forma, nunca fato.",
        "",
        "## Medidas",
        "",
        f"| medida | A: {nome_a} | B: {nome_b} | leitura |",
        "|---|---|---|---|",
    ]
    ma, mb = a.get("medidas", {}), b.get("medidas", {})
    iguais = diferentes = 0
    for chave in sorted(set(ma) & set(mb)):
        leitura = leitura_medida(ma[chave], mb[chave])
        iguais += leitura == "iguais"
        diferentes += leitura in {"A maior", "B maior"}
        linhas.append(f"| {chave} | {fmt(ma[chave])} | {fmt(mb[chave])} | {leitura} |")
    so_a, so_b = sorted(set(ma) - set(mb)), sorted(set(mb) - set(ma))
    if so_a or so_b:
        linhas += ["", f"Só em A: {', '.join(so_a) or 'nada'}. Só em B: {', '.join(so_b) or 'nada'}."]
    linhas += ["", "## Traços", "", f"| traço | A: {nome_a} | B: {nome_b} | leitura |", "|---|---|---|---|"]
    pa, pb = a.get("prevalencia", {}), b.get("prevalencia", {})
    fortes, divergem = [], []
    for chave in sorted(set(pa) & set(pb)):
        leitura = leitura_traco(pa[chave], pb[chave])
        if leitura == "padrão nos dois":
            fortes.append(chave)
        elif leitura == "divergem":
            divergem.append(chave)
        linhas.append(f"| {chave} | {fmt_traco(pa[chave])} | {fmt_traco(pb[chave])} | {leitura} |")
    ca, cb = a.get("curvas", {}), b.get("curvas", {})
    curvas = sorted(k for k in set(ca) & set(cb) if isinstance(ca[k], list) and isinstance(cb[k], list))
    if curvas:
        linhas += ["", "## Curvas por décimo", "", "| curva | A | B |", "|---|---|---|"]
        for chave in curvas:
            fa = " ".join("-" if v is None else f"{v:g}" for v in ca[chave])
            fb = " ".join("-" if v is None else f"{v:g}" for v in cb[chave])
            linhas.append(f"| {chave} | {fa} | {fb} |")
    linhas += [
        "",
        "## Resumo",
        "",
        f"- Medidas iguais: {iguais}; diferentes: {diferentes}.",
        f"- Padrão nos dois moldes: {', '.join(fortes) or 'nenhum'}.",
        f"- Traços que divergem: {', '.join(divergem) or 'nenhum'}.",
        "",
    ]
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("a", type=Path)
    parser.add_argument("b", type=Path)
    parser.add_argument("--nomes", nargs=2, metavar=("A", "B"))
    parser.add_argument("--saida", type=Path, help="arquivo .md; padrão: stdout")
    args = parser.parse_args(argv)
    a = json.loads(args.a.read_text(encoding="utf-8"))
    b = json.loads(args.b.read_text(encoding="utf-8"))
    nome_a, nome_b = args.nomes or (args.a.stem, args.b.stem)
    texto = comparar(a, b, nome_a, nome_b)
    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(texto, encoding="utf-8")
        print(f"comparação em {args.saida}")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
