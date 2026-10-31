"""Molde do nicho: as medidas da amostra resumidas em mediana, quartis e prevalência (ADR 031, parte B).

Uso:
  python3 -I molde.py <pasta do cache do nicho> [--notas <research_notes/<Título>/formato>]
                      [--grupo G [G ...]] [--assunto voce|obra|mundo|pensador] [--saida molde.json]

Lê o que os passos anteriores da skill já gravaram na pasta do cache: `amostra.tsv`, `medidas.csv`,
`janelas.csv`, `<id>.info.json` (capítulos) e `<id>.txt` (transcrição com tempo). Com `--notas`, lê também as
batidas marcadas por agente (`batidas/<id>.batidas.tsv`) e conta a estrutura com o `narrativa.py`.

Saída: `molde.json` com, para cada medida, mediana, q1, q3 e n (e o valor do terço de mais views e do de
menos, quando a amostra tem 6 ou mais vídeos); a prevalência de cada traço (quantos vídeos o têm) com a força
(`padrao` só com 8 ou mais vídeos e 80% ou mais; o resto é `indicio`); e as curvas por décimo. É forma, nunca
fato: nada daqui vira afirmação no roteiro.

Título do vídeo (coluna `titulo` da amostra, senão de `medidas.csv`; 2026-10-23): `titulo_video_chars` e
`titulo_video_palavras` medem o tamanho, `titulo_video_pergunta` conta os títulos com "?", e
`titulo_video_dito_s` diz em que segundo a fala já disse metade das palavras de conteúdo do título (traço
`titulo_video_dito`: em quantos vídeos isso acontece). `titulo_palavras` e `titulo_dito` são dos CAPÍTULOS.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import narrativa  # noqa: E402

VOCE = re.compile(r"\bvoc[êe]s?\b", re.I)
EU = re.compile(r"\beu\b", re.I)
ANO = re.compile(r"\b(1[5-9]\d\d|20[0-2]\d)\b")
PERGUNTA = re.compile(r"\?")
PROMESSA = re.compile(
    r"nesse v[íi]deo|neste v[íi]deo|hoje (a gente|eu) vou|vou te (mostrar|contar|explicar)"
    r"|a gente vai (ver|entender|falar)|vamos (ver|entender|falar)|eu quero (te )?(mostrar|contar|explicar)",
    re.I,
)
JANELA_TITULO_S = 20
MIN_LETRAS_TITULO = 4  # palavra de conteúdo do título: 4 letras ou mais, fora da lista abaixo
STOP_TITULO = frozenset({
    "como", "para", "pelo", "pela", "pelos", "pelas", "você", "voce", "vocês", "voces", "isso", "isto",
    "esse", "essa", "este", "esta", "aquele", "aquela", "mais", "menos", "muito", "tudo", "nada", "quando",
    "onde", "porque", "então", "ainda", "sobre", "entre", "até", "depois", "antes", "mesmo", "cada", "sempre",
    "nunca", "quem", "qual", "quais", "coisa", "coisas", "vídeo", "video", "parte", "episódio", "episodio",
    "minutos", "pode", "podem", "deve", "devem", "está", "estão", "foram", "sendo", "tinha", "teria", "fazer",
    "ouvir", "enquanto", "outra", "outro", "outras", "outros", "também", "assim", "aqui", "agora", "hoje",
    "anos", "todo", "toda", "todos", "todas", "primeiro", "primeira", "deveria", "devia", "deviam", "estava",
    "estavam", "gente", "certo", "certa", "nosso", "nossa", "ninguém", "ninguem", "alguém", "alguem",
})
DECIMOS = 10
MIN_PADRAO_N = 8
MIN_PADRAO_PCT = 80
MIN_TERCOS_N = 6

MEDIDAS_CSV = (
    "palavras_min", "cortes_min", "plano_medio_s", "voce_por_mil", "nos_por_mil", "eu_por_mil",
    "fonte_por_mil", "palavras_60s", "voce_60s", "cortes_60s",
)
ORIGEM = {
    "duracao_min": "amostra",
    "titulo_video_chars": "amostra", "titulo_video_palavras": "amostra",  # o título do VÍDEO
    "capitulos_n": "capitulos", "capitulo_min": "capitulos", "abertura_capitulo_s": "capitulos",
    "titulo_palavras": "capitulos",  # mediana de palavras dos títulos dos CAPÍTULOS, não do vídeo
    "primeiro_eu_s": "transcricao", "primeira_pergunta_s": "transcricao", "primeiro_voce_s": "transcricao",
    "primeiro_ano_s": "transcricao", "promessa_explicita_s": "transcricao",
    "titulo_video_dito_s": "transcricao",
}
MEDIDAS_BATIDAS = (
    "abertura_s", "blocos", "pct_caso", "pct_conceito", "pct_voce", "pct_narrador", "caso_antes_conceito_s",
    "primeiro_voce_s", "voce_por_10min", "confissoes", "ganchos_pagos", "chamadas",
)


def segundos(marca: str) -> float:
    total = 0.0
    for parte in marca.split(":"):
        total = total * 60 + float(parte)
    return total


def ler_transcricao(caminho: Path) -> list[tuple[float, str]]:
    linhas: list[tuple[float, str]] = []
    for linha in caminho.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\[(\d+(?::\d\d)+)\]\s*(.*)", linha)
        if m:
            linhas.append((segundos(m.group(1)), m.group(2)))
    return linhas


def primeiro(linhas: list[tuple[float, str]], padrao: re.Pattern[str]) -> float | None:
    for tempo, texto in linhas:
        if padrao.search(texto):
            return tempo
    return None


def resumo(valores: list[float]) -> dict[str, float | int]:
    xs = sorted(float(v) for v in valores)
    saida: dict[str, float | int] = {"mediana": round(statistics.median(xs), 1), "n": len(xs)}
    if len(xs) >= 2:
        q1, _, q3 = statistics.quantiles(xs, n=4)
        saida["q1"], saida["q3"] = round(q1, 1), round(q3, 1)
    return saida


def forca(com: int, n: int) -> str:
    return "padrao" if n >= MIN_PADRAO_N and 100 * com / n >= MIN_PADRAO_PCT else "indicio"


def ler_amostra(pasta: Path, amostra: Path | None = None) -> dict[str, dict[str, str]]:
    caminho = amostra or pasta / "amostra.tsv"
    if not caminho.exists():
        return {}
    with caminho.open(encoding="utf-8") as arquivo:
        return {linha["video_id"]: linha for linha in csv.DictReader(arquivo, delimiter="\t")}


def ler_csv(caminho: Path) -> list[dict[str, str]]:
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def abertura_por_capitulos(capitulos: list[dict]) -> float | None:
    if len(capitulos) < 2:
        return None
    primeiro_cap = capitulos[0]
    if float(primeiro_cap["start_time"]) == 0:
        return float(primeiro_cap["end_time"])
    return float(primeiro_cap["start_time"])


def assunto_do_titulo(titulo: str) -> list[str]:
    """Palavras de conteúdo do título do vídeo: 4 letras ou mais e fora da lista de palavras de função."""
    vistas: list[str] = []
    for w in re.findall(r"\w+", titulo.lower()):
        if len(w) >= MIN_LETRAS_TITULO and w not in STOP_TITULO and w not in vistas:
            vistas.append(w)
    return vistas


def titulo_video_dito_em(titulo: str, linhas: list[tuple[float, str]]) -> float | None:
    """Segundo em que a fala já disse metade das palavras de conteúdo do título (ao menos uma); None se não
    diz. Uma palavra conta quando a fala tem uma palavra que começa por ela ("navio" vale por "navios")."""
    palavras = assunto_do_titulo(titulo)
    if not palavras or not linhas:
        return None
    alvo = max(1, len(palavras) // 2)
    padroes = [re.compile(r"\b" + re.escape(w)) for w in palavras]
    fala = ""
    for tempo, texto in linhas:
        fala += " " + texto.lower()
        if sum(1 for p in padroes if p.search(fala)) >= alvo:
            return tempo
    return None


def titulo_dito(capitulo: dict, linhas: list[tuple[float, str]]) -> bool:
    palavras = [w for w in re.findall(r"\w+", capitulo["title"].lower()) if len(w) > 3]
    if not palavras:
        return False
    inicio = float(capitulo["start_time"])
    fala = " ".join(t.lower() for s, t in linhas if inicio - 5 <= s <= inicio + JANELA_TITULO_S)
    return sum(1 for w in palavras if w in fala) >= max(1, len(palavras) // 2)


def estrutura_dos_blocos(marcacao: narrativa.Marcacao) -> tuple[int, int, int, int]:
    """(blocos, blocos que abrem com caso, blocos com conceito, blocos em que há caso antes do conceito)."""
    blocos = sorted({b.bloco for b in marcacao.batidas if b.bloco >= 1})
    abre_caso = com_conceito = caso_antes = 0
    for bloco in blocos:
        longas = [b for b in marcacao.batidas if b.bloco == bloco and b.tipo in narrativa.LONGOS]
        if not longas:
            continue
        if longas[0].tipo == "CASO":
            abre_caso += 1
        indice = next((i for i, b in enumerate(longas) if b.tipo == "CONCEITO"), None)
        if indice is not None:
            com_conceito += 1
            if any(b.tipo == "CASO" for b in longas[:indice]):
                caso_antes += 1
    return len(blocos), abre_caso, com_conceito, caso_antes


def construir(
    pasta: Path, notas: Path | None, grupos: list[str], assunto: str | None, amostra_tsv: Path | None = None
) -> dict:
    amostra = ler_amostra(pasta, amostra_tsv)
    medidas_csv = {linha["video_id"]: linha for linha in ler_csv(pasta / "medidas.csv")}
    janelas: dict[str, list[dict[str, str]]] = defaultdict(list)
    for linha in ler_csv(pasta / "janelas.csv"):
        janelas[linha["video_id"]].append(linha)

    ids = set(amostra) | set(medidas_csv)
    if grupos:
        ids = {v for v in ids if amostra.get(v, {}).get("grupo") in grupos}
    idioma = {v: m.get("idioma", "") for v, m in medidas_csv.items()}
    ids = {v for v in ids if not idioma.get(v) or idioma[v].lower().startswith("pt")}

    marcacoes: dict[str, narrativa.Marcacao] = {}
    if notas is not None:
        for caminho in sorted((notas / "batidas").glob("*.batidas.tsv")):
            marcacao = narrativa.ler_batidas(caminho)
            if marcacao.video_id in ids or not amostra:
                marcacoes[marcacao.video_id] = marcacao
    if assunto:
        ids = {v for v, m in marcacoes.items() if m.cabecalho.get("assunto") == assunto}
        marcacoes = {v: m for v, m in marcacoes.items() if v in ids}

    valores: dict[str, dict[str, float]] = defaultdict(dict)  # medida -> video -> valor
    prevalencia: dict[str, dict[str, object]] = {}
    contagens: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # traço -> [com, n]
    curvas: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    canais: Counter[str] = Counter()
    views: dict[str, float] = {}

    for vid in sorted(ids):
        linha_amostra = amostra.get(vid, {})
        medida = medidas_csv.get(vid, {})
        canais[linha_amostra.get("canal") or medida.get("canal") or "?"] += 1
        views_txt = linha_amostra.get("views") or medida.get("views") or ""
        if views_txt:
            views[vid] = float(views_txt)
        duracao = float(linha_amostra.get("duracao_s") or medida.get("duracao_s") or 0)
        if duracao:
            valores["duracao_min"][vid] = duracao / 60
        titulo = (linha_amostra.get("titulo") or medida.get("titulo") or "").strip()
        if titulo:
            valores["titulo_video_chars"][vid] = len(titulo)
            valores["titulo_video_palavras"][vid] = len(titulo.split())
            contagens["titulo_video_pergunta"][1] += 1
            contagens["titulo_video_pergunta"][0] += int("?" in titulo)
        for chave in MEDIDAS_CSV:
            if medida.get(chave, "") != "":
                valores[chave][vid] = float(medida[chave])

        # curvas por décimo, a partir das janelas de 30 s
        rows = janelas.get(vid, [])
        if rows:
            por_decimo: dict[int, list[dict[str, str]]] = defaultdict(list)
            for row in rows:
                por_decimo[min(DECIMOS - 1, int(DECIMOS * int(row["janela"]) / len(rows)))].append(row)
            for decimo, rs in por_decimo.items():
                minutos = 0.5 * len(rs)
                for chave in ("voce", "eu", "fonte"):
                    total = sum(float(r[chave]) for r in rs)
                    curvas[f"{chave}_por_10min"][decimo].append(10 * total / minutos)
                # sem vídeo, sem cortes
                cortes = [float(r["cortes_min"]) for r in rs if r["cortes_min"] != ""]
                if cortes:
                    curvas["cortes_min"][decimo].append(statistics.mean(cortes))
                curvas["palavras_min"][decimo].append(statistics.mean(float(r["palavras_min"]) for r in rs))

        # capítulos e transcrição
        info = pasta / f"{vid}.info.json"
        capitulos: list[dict] = []
        if info.exists():
            capitulos = json.loads(info.read_text(encoding="utf-8")).get("chapters") or []
        transcricao = pasta / f"{vid}.txt"
        linhas = ler_transcricao(transcricao) if transcricao.exists() else []
        contagens["capitulos"][1] += 1
        if len(capitulos) >= 3:
            contagens["capitulos"][0] += 1
            valores["capitulos_n"][vid] = len(capitulos)
            valores["capitulo_min"][vid] = statistics.median(
                (float(c["end_time"]) - float(c["start_time"])) / 60 for c in capitulos
            )
            valores["titulo_palavras"][vid] = statistics.median(len(c["title"].split()) for c in capitulos)
            abertura = abertura_por_capitulos(capitulos)
            if abertura is not None:
                valores["abertura_capitulo_s"][vid] = abertura
            if linhas:
                for capitulo in capitulos:
                    contagens["titulo_dito"][1] += 1
                    contagens["titulo_dito"][0] += int(titulo_dito(capitulo, linhas))
        if linhas:
            for chave, padrao in (
                ("primeiro_eu_s", EU), ("primeira_pergunta_s", PERGUNTA), ("primeiro_voce_s", VOCE),
                ("primeiro_ano_s", ANO),
            ):
                tempo = primeiro(linhas, padrao)
                if tempo is not None:
                    valores[chave][vid] = tempo
            tempo = primeiro(linhas, PROMESSA)
            contagens["promessa_explicita"][1] += 1
            if tempo is not None:
                contagens["promessa_explicita"][0] += 1
                valores["promessa_explicita_s"][vid] = tempo
            if titulo:
                contagens["titulo_video_dito"][1] += 1
                tempo = titulo_video_dito_em(titulo, linhas)
                if tempo is not None:
                    contagens["titulo_video_dito"][0] += 1
                    valores["titulo_video_dito_s"][vid] = tempo

        # batidas
        marcacao = marcacoes.get(vid)
        if marcacao is not None:
            m = narrativa.medidas(marcacao)
            for chave in MEDIDAS_BATIDAS:
                if m.get(chave, "") != "":
                    valores[f"batidas_{chave}"][vid] = float(m[chave])
            posicoes = [float(p) for p in str(m["posicao_confissoes_pct"]).split() if p]
            if posicoes:
                valores["batidas_posicao_confissao_pct"][vid] = statistics.median(posicoes)
            for traco, tem in (
                ("confissao", int(m["confissoes"]) > 0), ("gancho_pago", int(m["ganchos_pagos"]) > 0),
                ("fecho_volta", bool(m["fecho_volta"])), ("fecho_contra_si", bool(m["fecho_contra_si"])),
                ("chamada", int(m["chamadas"]) > 0), ("capitulo_dito_na_fala", int(m["capitulos_ditos"]) > 0),
            ):
                contagens[traco][1] += 1
                contagens[traco][0] += int(tem)
            blocos, abre_caso, com_conceito, caso_antes = estrutura_dos_blocos(marcacao)
            contagens["bloco_abre_com_caso"][0] += abre_caso
            contagens["bloco_abre_com_caso"][1] += blocos
            contagens["caso_antes_do_conceito"][0] += caso_antes
            contagens["caso_antes_do_conceito"][1] += com_conceito

    ordem_views = sorted(views, key=views.get, reverse=True)  # type: ignore[arg-type]
    terco = len(ordem_views) // 3 if len(ordem_views) >= MIN_TERCOS_N else 0
    topo, base = set(ordem_views[:terco]), set(ordem_views[-terco:] if terco else [])

    medidas: dict[str, dict[str, object]] = {}
    for chave, por_video in sorted(valores.items()):
        item = resumo(list(por_video.values()))
        if terco:
            de_cima = [v for k, v in por_video.items() if k in topo]
            de_baixo = [v for k, v in por_video.items() if k in base]
            if de_cima and de_baixo:
                item["topo"] = round(statistics.median(de_cima), 1)
                item["base"] = round(statistics.median(de_baixo), 1)
        item["origem"] = ORIGEM.get(chave, "batidas" if chave.startswith("batidas_") else "medidas.csv")
        medidas[chave] = item
    unidades = {
        "titulo_dito": "capitulos", "bloco_abre_com_caso": "blocos", "caso_antes_do_conceito": "blocos",
    }
    for traco, (com, n) in sorted(contagens.items()):
        if n:
            prevalencia[traco] = {
                "com": com, "n": n, "pct": round(100 * com / n), "forca": forca(com, n),
                "unidade": unidades.get(traco, "videos"),
            }
    curvas_saida = {
        chave: [round(statistics.median(por_decimo[d]), 1) if por_decimo.get(d) else None
                for d in range(DECIMOS)]
        for chave, por_decimo in sorted(curvas.items())
    }
    return {
        "gerado_em": date.today().isoformat(),
        "pasta": str(pasta),
        "amostra": str(amostra_tsv) if amostra_tsv else str(pasta / "amostra.tsv"),
        "grupos": grupos,
        "assunto": assunto,
        "videos": {"n": len(ids), "ids": sorted(ids), "com_batidas": len(marcacoes), "canais": dict(canais)},
        "forca": {"padrao": f"n >= {MIN_PADRAO_N} e {MIN_PADRAO_PCT}% ou mais", "indicio": "o resto"},
        "medidas": medidas,
        "prevalencia": prevalencia,
        "curvas": {"decimos": DECIMOS, "n_videos": len({v for v in ids if janelas.get(v)}), **curvas_saida},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("pasta", type=Path)
    parser.add_argument("--notas", type=Path, help="pasta research_notes/<Título>/formato (com batidas/)")
    parser.add_argument("--grupo", nargs="+", default=[], help="só os grupos da amostra listados")
    parser.add_argument(
        "--assunto", choices=sorted(narrativa.ASSUNTOS), help="só os vídeos com batidas desse assunto",
    )
    parser.add_argument("--saida", type=Path, help="padrão: <pasta>/analise/molde.json")
    parser.add_argument(
        "--amostra", type=Path,
        help="outro TSV de amostra (video_id, grupo, canal, views…); padrão: <pasta>/amostra.tsv",
    )
    args = parser.parse_args(argv)

    molde = construir(args.pasta, args.notas, args.grupo, args.assunto, args.amostra)
    if molde["videos"]["n"] == 0:
        print(f"nenhum vídeo em {args.pasta} com esses filtros", file=sys.stderr)
        return 1
    saida = args.saida or args.pasta / "analise" / "molde.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(molde, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    v = molde["videos"]
    print(f"{v['n']} vídeo(s), {v['com_batidas']} com batidas, {len(molde['medidas'])} medidas, "
          f"{len(molde['prevalencia'])} traços → {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
