"""Conta a narrativa de cada vídeo a partir das batidas marcadas por um agente (`batidas.md`).

Uso:
  python3 -I narrativa.py medir <pasta com *.batidas.tsv> [--amostra amostra.tsv] [--saida <pasta>]
  python3 -I narrativa.py comparar <a.batidas.tsv> <b.batidas.tsv>
  python3 -I narrativa.py candidatos <transcrição .txt ou .srt> [--batidas <id>.batidas.tsv]

- `medir` grava `narrativa.csv` e `narrativa.md` (na pasta das batidas ou em `--saida`): fatia do tempo por
  tipo, tempo de caso antes do conceito em cada bloco, quando "você" entra, confissões, ganchos e fecho. Com
  `--amostra`, a tabela leva o grupo de cada vídeo.
- `comparar` mede quanto duas marcações do mesmo vídeo concordam: a fração do tempo com o mesmo tipo e, nas
  batidas de ponto, quantas caem a até 20 s uma da outra. Serve para saber se os tipos estão bem definidos.
- `candidatos` procura na transcrição frases que costumam marcar confissão, aplicação, ponte, gancho e
  chamada. É ajuda, não medida: a legenda automática não tem pontuação e erra palavras. Com `--batidas`, diz
  quantas batidas do agente têm um candidato perto e quantos candidatos caem perto de uma batida.

O script não lê o texto para interpretar: só conta o que o agente marcou. Mesmas batidas, mesma saída.
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

LONGOS = {"CASO", "CONCEITO", "APLICA", "PERGUNTA", "CONFISSAO", "OPINIAO", "FECHO-VOLTA", "FECHO-CONTRA-SI"}
PONTOS = {"CAPITULO", "PROMESSA", "PONTE", "GANCHO-PLANTA", "GANCHO-PAGA", "CHAMADA"}
TIPOS = LONGOS | PONTOS | {"FIM"}
JANELA_PONTO_S = 20
ASSUNTOS = {"voce", "obra", "mundo", "pensador"}

CANDIDATOS = {
    "CONFISSAO": re.compile(
        r"\beu (vou )?(admitir|confesso|confessar)\b|\beu (acreditei|achava|errei)\b|\bvergonha\b"
        r"|\beu (ia|tinha) (come[çc]ar|escrito)\b|\bestava escrito aqui\b",
        re.I,
    ),
    "APLICA": re.compile(
        r"\ba gente (faz|fica|jura|acha|ri|sabe)\b|\bvoc[êe] (faz|j[áa]|tamb[ée]m|nunca|sempre|mesmo)\b"
        r"|\bpensa (nas?|nos?|num|numa) ",
        re.I,
    ),
    "PONTE": re.compile(r"\bat[ée] que\b|\bs[óo] que a[íi]\b|\bmas antes\b|\bagora (vamos|a gente)\b", re.I),
    "GANCHO": re.compile(
        r"\bguarda (esse|essa|isso|o nome|essa imagem)\b|\blembra (do|da|dos|das|que)\b"
        r"|\bno final\b|\bdaqui a pouco\b|\bvolto nisso\b",
        re.I,
    ),
    "CHAMADA": re.compile(r"\binscrev|\bcomenta|\bcompartilh|\bmembro\b|\bcurt[ae]\b", re.I),
}
TIPO_DO_CANDIDATO = {
    "CONFISSAO": {"CONFISSAO"},
    "APLICA": {"APLICA", "PERGUNTA"},
    "PONTE": {"PONTE"},
    "GANCHO": {"GANCHO-PLANTA", "GANCHO-PAGA"},
    "CHAMADA": {"CHAMADA"},
}


@dataclass
class Batida:
    inicio: float
    tipo: str
    bloco: int
    ref: str
    resumo: str
    fim: float = 0.0


@dataclass
class Marcacao:
    video_id: str
    cabecalho: dict[str, str] = field(default_factory=dict)
    batidas: list[Batida] = field(default_factory=list)

    @property
    def duracao(self) -> float:
        return self.batidas[-1].inicio if self.batidas else 0.0


def segundos(texto: str) -> float:
    """`mm:ss`, `h:mm:ss` ou o tempo do SRT (`00:12:46,097`) em segundos."""
    partes = texto.strip().replace(",", ".").split(":")
    if not 2 <= len(partes) <= 3:
        raise ValueError(f"tempo inválido: {texto!r}")
    total = 0.0
    for parte in partes:
        total = total * 60 + float(parte)
    return total


def ler_batidas(caminho: Path) -> Marcacao:
    marcacao = Marcacao(video_id=caminho.name.removesuffix(".batidas.tsv"))
    for numero, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), start=1):
        if not linha.strip():
            continue
        if linha.startswith("#"):
            chave, _, valor = linha[1:].partition(":")
            chave, valor = chave.strip().lower(), valor.strip()
            if chave == "assunto":
                valor = valor.lower().replace("ê", "e")
                if valor not in ASSUNTOS:
                    raise ValueError(f"{caminho}:{numero}: assunto {valor!r} fora de {sorted(ASSUNTOS)}")
            marcacao.cabecalho[chave] = valor
            continue
        colunas = linha.split("\t")
        if len(colunas) < 3:
            raise ValueError(f"{caminho}:{numero}: esperava colunas separadas por tabulação")
        colunas += [""] * (5 - len(colunas))
        tipo = colunas[1].strip().upper()
        if tipo not in TIPOS:
            raise ValueError(f"{caminho}:{numero}: tipo desconhecido {tipo!r}")
        marcacao.batidas.append(
            Batida(segundos(colunas[0]), tipo, int(colunas[2] or 0), colunas[3].strip(), colunas[4].strip())
        )
    if not marcacao.batidas or marcacao.batidas[-1].tipo != "FIM":
        raise ValueError(f"{caminho}: a última linha precisa ser FIM")
    _duracoes(marcacao.batidas)
    return marcacao


def _duracoes(batidas: list[Batida]) -> None:
    """Batida longa dura até a próxima batida longa (ou o FIM); batida de ponto dura zero."""
    fim_do_video = batidas[-1].inicio
    for i, batida in enumerate(batidas):
        if batida.tipo not in LONGOS:
            batida.fim = batida.inicio
            continue
        seguintes = (b.inicio for b in batidas[i + 1 :] if b.tipo in LONGOS or b.tipo == "FIM")
        proxima = next(seguintes, fim_do_video)
        batida.fim = max(batida.inicio, proxima)


def medidas(marcacao: Marcacao) -> dict[str, object]:
    batidas = marcacao.batidas
    duracao = marcacao.duracao or 1.0
    por_tipo: dict[str, float] = {}
    for b in batidas:
        por_tipo[b.tipo] = por_tipo.get(b.tipo, 0.0) + (b.fim - b.inicio)

    def pct(*tipos: str) -> float:
        return round(100 * sum(por_tipo.get(t, 0.0) for t in tipos) / duracao, 1)

    def contagem(tipo: str) -> int:
        return sum(1 for b in batidas if b.tipo == tipo)

    caso_antes: list[float] = []
    conceito_primeiro = 0
    for bloco in sorted({b.bloco for b in batidas if b.bloco >= 1}):
        do_bloco = [b for b in batidas if b.bloco == bloco and b.tipo in LONGOS]
        primeiro_conceito = next((i for i, b in enumerate(do_bloco) if b.tipo == "CONCEITO"), None)
        if primeiro_conceito is None:
            continue
        antes = sum(b.fim - b.inicio for b in do_bloco[:primeiro_conceito] if b.tipo == "CASO")
        if antes == 0:
            conceito_primeiro += 1
        caso_antes.append(antes)

    plantados = {b.ref: b.inicio for b in batidas if b.tipo == "GANCHO-PLANTA" and b.ref}
    pagos = {b.ref: b.inicio for b in batidas if b.tipo == "GANCHO-PAGA" and b.ref}
    distancias = [(pagos[r] - plantados[r]) / 60 for r in plantados if r in pagos]
    primeiro_capitulo = next((b.inicio for b in batidas if b.bloco >= 1), duracao)
    primeiro_voce = next((b.inicio for b in batidas if b.tipo in {"APLICA", "PERGUNTA"}), None)
    blocos = {b.bloco for b in batidas if b.bloco >= 1}
    por_10 = 600 / duracao

    return {
        "video_id": marcacao.video_id,
        "assunto": marcacao.cabecalho.get("assunto", ""),
        "duracao_min": round(duracao / 60, 1),
        "abertura_s": round(primeiro_capitulo),
        "blocos": len(blocos),
        "capitulos_ditos": contagem("CAPITULO"),
        "pct_caso": pct("CASO"),
        "pct_conceito": pct("CONCEITO"),
        "pct_voce": pct("APLICA", "PERGUNTA"),
        "pct_narrador": pct("CONFISSAO", "OPINIAO"),
        "pct_fecho": pct("FECHO-VOLTA", "FECHO-CONTRA-SI"),
        "caso_antes_conceito_s": round(statistics.median(caso_antes)) if caso_antes else "",
        "blocos_conceito_primeiro": conceito_primeiro,
        "primeiro_voce_s": round(primeiro_voce) if primeiro_voce is not None else "",
        "voce_por_10min": round((contagem("APLICA") + contagem("PERGUNTA")) * por_10, 1),
        "confissoes": contagem("CONFISSAO"),
        "posicao_confissoes_pct": " ".join(
            str(round(100 * b.inicio / duracao)) for b in batidas if b.tipo == "CONFISSAO"
        ),
        "ganchos_plantados": len(plantados),
        "ganchos_pagos": sum(1 for r in plantados if r in pagos),
        "gancho_distancia_min": round(statistics.mean(distancias), 1) if distancias else "",
        "fecho_volta": int(contagem("FECHO-VOLTA") > 0),
        "fecho_contra_si": int(contagem("FECHO-CONTRA-SI") > 0),
        "chamadas": contagem("CHAMADA"),
        "tese": marcacao.cabecalho.get("tese", ""),
    }


def ler_grupos(amostra: Path | None) -> dict[str, str]:
    if amostra is None:
        return {}
    with amostra.open(encoding="utf-8") as arquivo:
        linhas = csv.DictReader(arquivo, delimiter="\t")
        return {linha["video_id"]: linha.get("grupo", "") for linha in linhas}


def tabela_md(linhas: list[dict[str, object]]) -> str:
    colunas = [
        ("video_id", "vídeo"),
        ("grupo", "grupo"),
        ("assunto", "assunto"),
        ("duracao_min", "min"),
        ("abertura_s", "abertura (s)"),
        ("pct_caso", "% caso"),
        ("pct_conceito", "% conceito"),
        ("pct_voce", "% você"),
        ("pct_narrador", "% narrador"),
        ("caso_antes_conceito_s", "caso antes do conceito (s)"),
        ("primeiro_voce_s", "1º você (s)"),
        ("voce_por_10min", "você/10 min"),
        ("confissoes", "confissões"),
        ("ganchos_pagos", "ganchos pagos"),
        ("fecho_volta", "fecho volta"),
        ("fecho_contra_si", "fecho contra si"),
        ("chamadas", "chamadas"),
    ]
    saida = [
        "# Narrativa por vídeo",
        "",
        "Contado por `narrativa.py medir` sobre as batidas marcadas por agente (`batidas.md`). "
        "\"% você\" = APLICA + PERGUNTA; \"% narrador\" = CONFISSAO + OPINIAO; "
        "\"caso antes do conceito\" é a mediana dos blocos.",
        "",
        "| " + " | ".join(nome for _, nome in colunas) + " |",
        "|" + "---|" * len(colunas),
    ]
    for linha in linhas:
        saida.append("| " + " | ".join(str(linha.get(chave, "")) for chave, _ in colunas) + " |")
    saida += ["", "## Tese de cada vídeo", ""]
    saida += [f"- **{linha['video_id']}** ({linha['assunto']}): {linha['tese']}" for linha in linhas]
    return "\n".join(saida) + "\n"


def cmd_medir(args: argparse.Namespace) -> int:
    pasta = Path(args.pasta)
    arquivos = sorted(pasta.glob("*.batidas.tsv"))
    if not arquivos:
        print(f"nenhum *.batidas.tsv em {pasta}", file=sys.stderr)
        return 1
    grupos = ler_grupos(Path(args.amostra) if args.amostra else None)
    linhas = []
    for arquivo in arquivos:
        linha = medidas(ler_batidas(arquivo))
        linha["grupo"] = grupos.get(str(linha["video_id"]), "")
        linhas.append(linha)
    saida = Path(args.saida) if args.saida else pasta
    saida.mkdir(parents=True, exist_ok=True)
    with (saida / "narrativa.csv").open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    (saida / "narrativa.md").write_text(tabela_md(linhas), encoding="utf-8")
    print(f"{len(linhas)} vídeos → {saida / 'narrativa.csv'} e {saida / 'narrativa.md'}")
    return 0


def tipo_no_segundo(marcacao: Marcacao, segundo: float) -> str:
    for batida in marcacao.batidas:
        if batida.tipo in LONGOS and batida.inicio <= segundo < batida.fim:
            return batida.tipo
    return "-"


def comparar(a: Marcacao, b: Marcacao) -> dict[str, object]:
    duracao = int(min(a.duracao, b.duracao))
    iguais = 0
    trocas: dict[tuple[str, str], int] = {}
    for segundo in range(duracao):
        ta, tb = tipo_no_segundo(a, segundo + 0.5), tipo_no_segundo(b, segundo + 0.5)
        if ta == tb:
            iguais += 1
        else:
            trocas[(ta, tb)] = trocas.get((ta, tb), 0) + 1
    pontos = {}
    for tipo in sorted(PONTOS | {"CONFISSAO", "APLICA", "PERGUNTA"}):
        em_a = [x.inicio for x in a.batidas if x.tipo == tipo]
        em_b = [x.inicio for x in b.batidas if x.tipo == tipo]
        if em_a or em_b:
            casados = sum(1 for t in em_a if any(abs(t - u) <= JANELA_PONTO_S for u in em_b))
            pontos[tipo] = (len(em_a), len(em_b), casados)
    return {
        "segundos": duracao,
        "concordancia_pct": round(100 * iguais / duracao, 1) if duracao else 0.0,
        "trocas": sorted(trocas.items(), key=lambda item: -item[1])[:5],
        "pontos": pontos,
        "assunto": (a.cabecalho.get("assunto", ""), b.cabecalho.get("assunto", "")),
        "blocos": (len({x.bloco for x in a.batidas}), len({x.bloco for x in b.batidas})),
    }


def cmd_comparar(args: argparse.Namespace) -> int:
    resultado = comparar(ler_batidas(Path(args.a)), ler_batidas(Path(args.b)))
    print(f"Tempo com o mesmo tipo: {resultado['concordancia_pct']}% de {resultado['segundos']} s")
    print(f"Assunto: {resultado['assunto'][0]} × {resultado['assunto'][1]}")
    print(f"Blocos (contando a abertura): {resultado['blocos'][0]} × {resultado['blocos'][1]}")
    print("Maiores trocas (A → B, segundos):")
    for (ta, tb), n in resultado["trocas"]:
        print(f"  {ta} → {tb}: {n}")
    print(f"Batidas a até {JANELA_PONTO_S} s uma da outra (A, B, casadas):")
    for tipo, (na, nb, casados) in resultado["pontos"].items():
        print(f"  {tipo}: {na}, {nb}, {casados}")
    return 0


def ler_transcricao(caminho: Path) -> list[tuple[float, str]]:
    """Linhas `[mm:ss] texto` do `medir.py` ou blocos de um SRT, como (segundo, texto)."""
    texto = caminho.read_text(encoding="utf-8")
    linhas: list[tuple[float, str]] = []
    if caminho.suffix.lower() == ".srt":
        for bloco in re.split(r"\n\s*\n", texto.strip()):
            partes = bloco.splitlines()
            tempo = next((p for p in partes if "-->" in p), None)
            if tempo is None:
                continue
            fala = " ".join(p for p in partes[partes.index(tempo) + 1 :])
            linhas.append((segundos(tempo.split("-->")[0]), fala))
        return linhas
    for linha in texto.splitlines():
        achado = re.match(r"\[(\d+(?::\d+){1,2})\]\s*(.*)", linha)
        if achado:
            linhas.append((segundos(achado.group(1)), achado.group(2)))
    return linhas


def candidatos(linhas: list[tuple[float, str]]) -> list[tuple[float, str, str]]:
    """Cada linha é lida junto com a seguinte, porque a legenda corta a frase no meio."""
    achados = []
    for i, (inicio, fala) in enumerate(linhas):
        trecho = fala + " " + (linhas[i + 1][1] if i + 1 < len(linhas) else "")
        for tipo, padrao in CANDIDATOS.items():
            if padrao.search(trecho):
                achados.append((inicio, tipo, trecho.strip()))
    return achados


def cmd_candidatos(args: argparse.Namespace) -> int:
    achados = candidatos(ler_transcricao(Path(args.transcricao)))
    if not args.batidas:
        for inicio, tipo, trecho in achados:
            print(f"{int(inicio // 60):02d}:{int(inicio % 60):02d}\t{tipo}\t{trecho[:100]}")
        return 0
    marcacao = ler_batidas(Path(args.batidas))
    print(
        f"Candidatos × batidas do agente, a até {JANELA_PONTO_S} s "
        "(batidas com candidato perto / candidatos perto de uma batida):"
    )
    for tipo, tipos_do_agente in TIPO_DO_CANDIDATO.items():
        do_agente = [b.inicio for b in marcacao.batidas if b.tipo in tipos_do_agente]
        do_script = [inicio for inicio, t, _ in achados if t == tipo]
        cobertas = sum(1 for t in do_agente if any(abs(t - u) <= JANELA_PONTO_S for u in do_script))
        certos = sum(1 for u in do_script if any(abs(t - u) <= JANELA_PONTO_S for t in do_agente))
        print(f"  {tipo}: {cobertas}/{len(do_agente)} batidas, {certos}/{len(do_script)} candidatos")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="comando", required=True)
    p_medir = sub.add_parser("medir")
    p_medir.add_argument("pasta")
    p_medir.add_argument("--amostra")
    p_medir.add_argument("--saida")
    p_medir.set_defaults(func=cmd_medir)
    p_comparar = sub.add_parser("comparar")
    p_comparar.add_argument("a")
    p_comparar.add_argument("b")
    p_comparar.set_defaults(func=cmd_comparar)
    p_cand = sub.add_parser("candidatos")
    p_cand.add_argument("transcricao")
    p_cand.add_argument("--batidas")
    p_cand.set_defaults(func=cmd_candidatos)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
