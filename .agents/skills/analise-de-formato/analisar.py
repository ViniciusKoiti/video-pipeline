"""Cruza as medidas da amostra com o desempenho e compara com um episódio nosso.

Uso:
  python -I analisar.py <pasta> <amostra.tsv> [--episodio <episode.json>]

`python` é qualquer Python com pandas: `uv run --no-project --with pandas python`, ou um ambiente que já o
tenha.

Lê `medidas.csv` e `janelas.csv` (de `medir.py`) e o grupo de cada vídeo em `amostra.tsv` (de `amostra.py`;
o grupo
`-idioma` e os incluídos com anime contam como `H`). Grava em `<pasta>/analise/`:
- `correlacoes.csv`: correlação de Spearman de cada medida com log(views) e com views por inscrito, por grupo;
- `tercos.csv`: mediana de cada medida no terço de mais views e no de menos, por grupo;
- `curva.csv`: palavras/min, cortes/min e "você", "eu" e fonte por mil palavras em cada décimo do vídeo,
  para o
  terço de cima e o de baixo;
- `episodio.csv`: as mesmas medidas do nosso `episode.json`, com planos por minuto no lugar de cortes;
- `resumo.md`: as tabelas acima em Markdown, com o tamanho de cada grupo.

Mesmas entradas, mesma saída. Com menos de 8 vídeos num grupo, a correlação sai, mas o resumo avisa que é só
descrição. Só entram vídeos falados em português (`idioma` de `medidas.csv`): legenda traduzida não mede a
fala.
pandas (BSD-3) é usado só por esta skill, fora do `.venv` do projeto.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import pandas as pd

MEASURES = [
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
    "capitulos",
]
SPOKEN = {
    "voce": re.compile(r"\b(você|vocês)\b", re.I),
    "nos": re.compile(r"\b(a gente|nós|nosso|nossa|nossos|nossas)\b", re.I),
    "eu": re.compile(r"\b(eu|meu|minha|pra mim|para mim|acho)\b", re.I),
    "fonte": re.compile(
        r"\b(segundo|de acordo com|estudo|estudos|pesquisa|pesquisas|pesquisadores|artigo)\b", re.I
    ),
}
MIN_GROUP = 8


def markdown(frame: pd.DataFrame) -> str:
    """Tabela Markdown sem depender do tabulate."""
    cells = [["" if pd.isna(v) else str(v) for v in row] for row in frame.itertuples(index=False)]
    header = "| " + " | ".join(map(str, frame.columns)) + " |"
    rule = "|" + "|".join("---" for _ in frame.columns) + "|"
    return "\n".join([header, rule, *("| " + " | ".join(r) + " |" for r in cells)])


def load(folder: Path, sample: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    videos = pd.read_csv(folder / "medidas.csv")
    groups = pd.read_csv(sample, sep="\t", dtype=str)[["video_id", "grupo"]]
    groups["grupo"] = groups["grupo"].replace({"-idioma": "H", "-": "H"}).fillna("H")
    videos = videos.merge(groups.drop_duplicates("video_id"), on="video_id", how="inner")
    videos = videos[(videos["palavras"] > 0) & videos["idioma"].fillna("pt").str.startswith("pt")].copy()
    videos["log_views"] = videos["views"].apply(lambda v: math.log10(v) if v and v > 0 else None)
    videos["views_por_inscrito"] = videos["views"] / videos["inscritos"].where(videos["inscritos"] > 0)
    windows = pd.read_csv(folder / "janelas.csv").merge(
        videos[["video_id", "grupo", "log_views"]], on="video_id"
    )
    return videos, windows


def terciles(videos: pd.DataFrame) -> pd.DataFrame:
    def label(group: pd.DataFrame) -> pd.Series:
        ranks = group["log_views"].rank(method="first", pct=True)
        return pd.cut(ranks, [0, 1 / 3, 2 / 3, 1], labels=["baixo", "meio", "alto"])

    return videos.groupby("grupo", group_keys=False).apply(label)


def correlations(videos: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group, frame in videos.groupby("grupo"):
        for measure in MEASURES:
            rows.append(
                {
                    "grupo": group,
                    "medida": measure,
                    "n": int(frame[measure].notna().sum()),
                    "rho_log_views": round(frame[measure].corr(frame["log_views"], method="spearman"), 2),
                    "rho_views_por_inscrito": round(
                        frame[measure].corr(frame["views_por_inscrito"], method="spearman"), 2
                    ),
                }
            )
    return pd.DataFrame(rows)


def curve(windows: pd.DataFrame, videos: pd.DataFrame) -> pd.DataFrame:
    frame = windows.merge(videos[["video_id", "terco"]], on="video_id")
    frame = frame[frame["terco"].isin(["alto", "baixo"])].copy()
    frame["decimo"] = (frame["posicao"] * 10).clip(upper=9.999).astype(int) + 1
    summed = frame.groupby(["grupo", "terco", "decimo"], observed=True).agg(
        palavras=("palavras", "sum"),
        voce=("voce", "sum"),
        eu=("eu", "sum"),
        fonte=("fonte", "sum"),
        palavras_min=("palavras_min", "median"),
        cortes_min=("cortes_min", "median"),
        janelas=("janela", "count"),
    )
    for name in ("voce", "eu", "fonte"):
        summed[f"{name}_por_mil"] = (summed[name] / summed["palavras"].clip(lower=1) * 1000).round(1)
    return summed.drop(columns=["voce", "eu", "fonte"]).reset_index()


def episode_measures(path: Path) -> pd.DataFrame:
    episode = json.loads(path.read_text(encoding="utf-8"))
    scenes = episode["scenes"]
    duration = sum(s["duration_ms"] for s in scenes) / 1000
    text = " ".join(re.sub(r"<[^>]+>", " ", s["narration"]) for s in scenes)
    words = len(text.split())
    opening = " ".join(re.sub(r"<[^>]+>", " ", s["narration"]) for s in scenes if s["start_ms"] < 60_000)
    shots = sum(len(s["shots"]) for s in scenes)
    row = {
        "episodio": episode.get("episode_id"),
        "duracao_s": round(duration),
        "palavras": words,
        "palavras_min": round(words / duration * 60),
        "planos_min": round(shots / duration * 60, 1),
        "plano_medio_s": round(duration / max(shots, 1), 1),
        "palavras_60s": len(opening.split()),
        "voce_60s": len(SPOKEN["voce"].findall(opening)),
    }
    for name, pattern in SPOKEN.items():
        row[f"{name}_por_mil"] = round(len(pattern.findall(text)) / max(words, 1) * 1000, 1)
    return pd.DataFrame([row])


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("pasta")
    parser.add_argument("amostra")
    parser.add_argument("--episodio")
    args = parser.parse_args()
    folder = Path(args.pasta)
    out = folder / "analise"
    out.mkdir(exist_ok=True)

    videos, windows = load(folder, Path(args.amostra))
    videos["terco"] = terciles(videos)
    corr = correlations(videos)
    thirds = (
        videos[videos["terco"].isin(["alto", "baixo"])]
        .groupby(["grupo", "terco"], observed=True)[MEASURES + ["views"]]
        .median()
        .round(1)
        .reset_index()
    )
    curves = curve(windows, videos)
    corr.to_csv(out / "correlacoes.csv", index=False)
    thirds.to_csv(out / "tercos.csv", index=False)
    curves.to_csv(out / "curva.csv", index=False)

    lines = ["# Análise de formato: medidas da amostra", ""]
    sizes = videos.groupby("grupo").size()
    lines.append("Vídeos por grupo: " + ", ".join(f"{g} = {n}" for g, n in sizes.items()) + ".")
    small = [g for g, n in sizes.items() if n < MIN_GROUP]
    if small:
        lines.append(
            f"Grupos com menos de {MIN_GROUP} vídeos ({', '.join(small)}): só descrição, sem conclusão."
        )
    lines += [
        "",
        "## Terço de mais views × terço de menos (medianas)",
        "",
        markdown(thirds),
        "",
        "## Correlação de Spearman com o desempenho",
        "",
        markdown(corr.sort_values(["grupo", "rho_log_views"])),
        "",
        "## Curva ao longo do vídeo (décimos)",
        "",
        markdown(curves),
        "",
    ]
    if args.episodio:
        ours = episode_measures(Path(args.episodio))
        ours.to_csv(out / "episodio.csv", index=False)
        lines += [
            "## Nosso episódio, nas mesmas medidas",
            "",
            "Planos por minuto vêm do `episode.json` e são comparáveis a cortes por minuto.",
            "",
            markdown(ours),
            "",
        ]
    (out / "resumo.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"análise em {out}: {len(videos)} vídeos, {len(windows)} janelas")


if __name__ == "__main__":
    main()
