"""Quais vídeos da amostra têm uma forma que a pipeline reproduz (ADR 031): sem apresentador e com base de
imagem que a gente faz (banco, foto de arquivo, pintura, texto, ilustração, quadro parado).

Uso:
  python3 -I reproduzivel.py <pasta do cache> <imagem.tsv> [<imagem2.tsv> ...]
                             [--minimo-views 400000] [--grupo TOPO] [--saida <pasta>/analise/reproduzivel]

`imagem.tsv` é a leitura das folhas de quadros feita por subagente (passo 4d da skill), com as colunas
`video_id`, `apresentador` (nenhum | real | desenhado | avatar), `quadros_com_apresentador`, `base_principal`,
`pct_base_principal`, `base_secundaria`, `texto_na_tela`, `movimento`, `nota`. A regra do que é reproduzível
fica aqui, não no agente: ele só observa.

Saída: `reproduzivel.tsv` (uma linha por vídeo, com canal, views e o veredito) e `amostra-topo.tsv`, a amostra
dos reproduzíveis em português com views acima do mínimo, no formato que o `molde.py --amostra` lê.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

BASES_OK = frozenset(
    {"banco_de_imagens", "foto_arquivo", "ilustracao_propria", "texto_grafico", "pintura", "anime_parado"}
)
BASES_NAO = frozenset({"anime_movimento", "gameplay", "filme_live_action"})
MINIMO_VIEWS = 400_000


def veredito(apresentador: str, base: str, secundaria: str) -> str:
    if apresentador and apresentador != "nenhum":
        return "nao: apresentador"
    if base in BASES_NAO:
        return "nao: base"
    if base in BASES_OK:
        return "sim" if secundaria not in BASES_NAO else "parcial: base secundária"
    if base == "misto":
        return "parcial: misto"
    return "sem leitura"


def ler_imagem(caminhos: list[Path]) -> dict[str, dict[str, str]]:
    linhas: dict[str, dict[str, str]] = {}
    for caminho in caminhos:
        with caminho.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                limpo = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
                if limpo.get("video_id"):
                    limpo["origem"] = caminho.name
                    linhas[limpo["video_id"]] = limpo
    return linhas


def metadados(pasta: Path) -> dict[str, dict[str, object]]:
    meta: dict[str, dict[str, object]] = {}
    idioma = {}
    medidas = pasta / "medidas.csv"
    if medidas.exists():
        with medidas.open(encoding="utf-8") as fh:
            idioma = {r["video_id"]: r.get("idioma", "") for r in csv.DictReader(fh)}
    for info in sorted(pasta.glob("*.info.json")):
        d = json.loads(info.read_text(encoding="utf-8"))
        meta[d["id"]] = {
            "canal": d.get("channel", ""), "views": int(d.get("view_count") or 0),
            "duracao_s": int(d.get("duration") or 0), "titulo": d.get("title", ""),
            "idioma": idioma.get(d["id"], d.get("language") or ""),
        }
    return meta


def tabela(pasta: Path, imagens: list[Path]) -> list[dict[str, object]]:
    meta = metadados(pasta)
    linhas = []
    for vid, leitura in ler_imagem(imagens).items():
        m = meta.get(vid, {})
        duracao_s = int(m.get("duracao_s") or 0)
        campos = (
            "apresentador", "quadros_com_apresentador", "base_principal", "pct_base_principal",
            "base_secundaria", "texto_na_tela", "movimento",
        )
        linha: dict[str, object] = {
            "video_id": vid, "canal": m.get("canal", "?"), "views": m.get("views", 0),
            "duracao_s": duracao_s, "duracao_min": round(duracao_s / 60, 1), "idioma": m.get("idioma", ""),
        }
        linha.update({campo: leitura.get(campo, "") for campo in campos})
        linha["reproduzivel"] = veredito(
            str(linha["apresentador"]), str(linha["base_principal"]), str(linha["base_secundaria"])
        )
        linha["origem"], linha["nota"] = leitura.get("origem", ""), leitura.get("nota", "")
        linha["titulo"] = m.get("titulo", "")
        linhas.append(linha)
    linhas.sort(key=lambda r: -int(r["views"] or 0))
    return linhas


def topo(linhas: list[dict[str, object]], minimo_views: int) -> list[dict[str, object]]:
    return [
        r for r in linhas
        if r["reproduzivel"] == "sim" and int(r["views"] or 0) >= minimo_views
        and (not r["idioma"] or str(r["idioma"]).lower().startswith("pt"))
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pasta", type=Path)
    parser.add_argument("imagem", type=Path, nargs="+", help="TSV(s) da leitura das folhas")
    parser.add_argument("--minimo-views", type=int, default=MINIMO_VIEWS)
    parser.add_argument("--grupo", default="TOPO", help="nome do grupo na amostra de saída")
    parser.add_argument("--saida", type=Path, help="pasta; padrão: <pasta>/analise/reproduzivel")
    args = parser.parse_args(argv)

    linhas = tabela(args.pasta, args.imagem)
    if not linhas:
        print("nenhuma linha de leitura de imagem", file=sys.stderr)
        return 1
    saida = args.saida or args.pasta / "analise" / "reproduzivel"
    saida.mkdir(parents=True, exist_ok=True)
    cols = list(linhas[0].keys())
    with (saida / "reproduzivel.tsv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t")
        w.writeheader()
        w.writerows(linhas)
    escolhidos = topo(linhas, args.minimo_views)
    with (saida / "amostra-topo.tsv").open("w", encoding="utf-8", newline="") as fh:
        fh.write("video_id\tgrupo\tcanal\tviews\tduracao_s\tmotivo\ttitulo\n")
        for r in escolhidos:
            motivo = f"reproduzível sem apresentador, views >= {args.minimo_views}"
            fh.write(
                f"{r['video_id']}\t{args.grupo}\t{r['canal']}\t{r['views']}\t{r['duracao_s']}"
                f"\t{motivo}\t{r['titulo']}\n"
            )
    contagem = Counter(str(r["reproduzivel"]).split(":")[0] for r in linhas)
    print(
        f"{len(linhas)} vídeos lidos: {dict(contagem)}; {len(escolhidos)} no grupo {args.grupo} "
        f"(views >= {args.minimo_views}) → {saida}"
    )
    for r in escolhidos:
        canal = str(r["canal"])[:24]
        print(f"  {r['video_id']}  {canal:24s} {int(r['views'] or 0):>10,}  {r['base_principal']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
