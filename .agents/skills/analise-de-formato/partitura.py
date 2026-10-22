"""Partitura do episódio: o molde do nicho escalado para a duração de um episódio (ADR 031, parte B).

Uso:
  python3 -I partitura.py <molde.json> --duracao <min> [--assunto voce|obra|mundo|pensador] [--blocos N]
                          [--titulo "..."] [--episodio data/episodes/<id> | --saida partitura.md]
                          [--sobrescrever]

Escreve `partitura.md`: uma linha do tempo com as casas que o molde ocupa (abertura, blocos, confissão,
gancho, fecho), o que vale dentro de cada bloco, as curvas por décimo já no tamanho deste episódio e os alvos
para medir o rascunho depois (batidas cegas + `narrativa.py`). Com `--episodio`, grava a partitura na pasta do
episódio e copia o molde datado para lá (`molde.json`), no desenho da ADR 018. Não sobrescreve sem
`--sobrescrever`.

Regra de escala: os marcos dos primeiros segundos são absolutos (o molde os mede em segundos desde o início);
a abertura e os blocos são proporcionais à duração, com blocos do tamanho do molde (menos blocos, não blocos
menores); o último décimo é o fecho. É forma, nunca fato.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ASSUNTOS = ("voce", "obra", "mundo", "pensador")
LIMIAR_CASA_PCT = 50  # um traço vira casa da partitura quando metade ou mais dos vídeos o tem
ABERTURA_PADRAO_PCT = 0.12


def mmss(segundos: float) -> str:
    segundos = max(0, int(round(segundos)))
    return f"{segundos // 60}:{segundos % 60:02d}"


def medida(molde: dict, chave: str) -> dict | None:
    return molde.get("medidas", {}).get(chave)


def mediana(molde: dict, chave: str, padrao: float | None = None) -> float | None:
    item = medida(molde, chave)
    return float(item["mediana"]) if item else padrao


def traco(molde: dict, chave: str) -> dict | None:
    return molde.get("prevalencia", {}).get(chave)


def descreve(item: dict | None, unidade: str = "") -> str:
    if not item:
        return "sem dado"
    partes = [f"mediana {item['mediana']:g}{unidade}"]
    if "q1" in item:
        partes.append(f"q1 {item['q1']:g}, q3 {item['q3']:g}")
    partes.append(f"n {item['n']}")
    return ", ".join(partes)


def descreve_traco(item: dict | None) -> str:
    if not item:
        return "sem dado"
    return f"{item['com']} de {item['n']} {item['unidade']} ({item['pct']}%, {item['forca']})"


def tem_casa(item: dict | None) -> bool:
    return bool(item) and int(item["pct"]) >= LIMIAR_CASA_PCT


def plano(molde: dict, duracao_min: float, blocos_pedidos: int | None = None) -> dict:
    """Tempos da partitura para esta duração."""
    total = duracao_min * 60
    duracao_molde = mediana(molde, "duracao_min")
    abertura_molde = mediana(molde, "abertura_capitulo_s") or mediana(molde, "batidas_abertura_s")
    if abertura_molde and duracao_molde:
        abertura = min(abertura_molde, total * abertura_molde / (duracao_molde * 60))
    elif abertura_molde:
        abertura = min(abertura_molde, total * ABERTURA_PADRAO_PCT)
    else:
        abertura = total * ABERTURA_PADRAO_PCT
    fecho = total / 10
    corpo = max(0.0, total - abertura - fecho)
    bloco_molde_min = mediana(molde, "capitulo_min")
    if blocos_pedidos:
        blocos = blocos_pedidos
    elif bloco_molde_min:
        blocos = max(2, round(corpo / 60 / bloco_molde_min))
    else:
        blocos = max(2, int(mediana(molde, "batidas_blocos", 4) or 4))
    duracao_bloco = corpo / blocos if blocos else corpo
    confissao_pct = mediana(molde, "batidas_posicao_confissao_pct")
    return {
        "total_s": total,
        "abertura_s": abertura,
        "fecho_inicio_s": total - fecho,
        "blocos": blocos,
        "bloco_s": duracao_bloco,
        "confissao_s": total * confissao_pct / 100 if confissao_pct is not None else None,
    }


def linha_do_tempo(molde: dict, p: dict) -> list[tuple[str, str, str]]:
    """(tempo, casa, o que o molde diz)."""
    linhas: list[tuple[str, str, str]] = []
    marcos = [
        ("primeiro_eu_s", 'primeiro "eu"'),
        ("primeira_pergunta_s", "primeira pergunta"),
        ("primeiro_voce_s", 'primeiro "você"'),
        ("primeiro_ano_s", "primeiro ano ou data"),
    ]
    teto = p["total_s"] / 4
    com_dado = [(chave, nome, medida(molde, chave)) for chave, nome in marcos]
    for _chave, nome, item in sorted((m for m in com_dado if m[2]), key=lambda m: float(m[2]["mediana"])):
        tempo = min(float(item["mediana"]), teto)
        linhas.append((f"até {mmss(tempo)}", nome, descreve(item, " s")))
    linhas.append((
        f"0:00–{mmss(p['abertura_s'])}", "abertura: o caso que abre, antes do primeiro bloco",
        f"abertura do molde {descreve(medida(molde, 'abertura_capitulo_s'), ' s')}; "
        f"promessa dita com todas as letras em {descreve_traco(traco(molde, 'promessa_explicita'))}: "
        "a promessa pode vir pelo caso",
    ))
    gancho = traco(molde, "gancho_pago")
    if tem_casa(gancho):
        linhas.append((f"~{mmss(p['abertura_s'])}", "gancho plantado (pago no último bloco)",
                       f"gancho pago em {descreve_traco(gancho)}"))
    inicio = p["abertura_s"]
    for numero in range(1, p["blocos"] + 1):
        fim = inicio + p["bloco_s"]
        linhas.append((f"{mmss(inicio)}–{mmss(fim)}", f"bloco {numero}", "ver \"Dentro de cada bloco\""))
        inicio = fim
    confissao = traco(molde, "confissao")
    if tem_casa(confissao) and p["confissao_s"] is not None:
        linhas.append((f"~{mmss(p['confissao_s'])}", "confissão do narrador",
                       f"{descreve_traco(confissao)}; posição "
                       f"{descreve(medida(molde, 'batidas_posicao_confissao_pct'), '%')}; "
                       f"quantidade {descreve(medida(molde, 'batidas_confissoes'))}"))
    if tem_casa(gancho):
        linhas.append((f"bloco {p['blocos']}", "gancho pago", "o que ficou plantado na abertura volta"))
    fecho_volta = traco(molde, "fecho_volta")
    contra_si = traco(molde, "fecho_contra_si")
    fecho_txt = []
    if tem_casa(fecho_volta):
        fecho_txt.append(f"o fim retoma a cena da abertura em {descreve_traco(fecho_volta)}")
    if tem_casa(contra_si):
        fecho_txt.append(f"a tese volta contra o narrador em {descreve_traco(contra_si)}")
    chamada = traco(molde, "chamada")
    if chamada:
        verbo = "chamada" if tem_casa(chamada) else "quase sem chamada"
        fecho_txt.append(f"{verbo}: {descreve_traco(chamada)}")
    linhas.append((f"{mmss(p['fecho_inicio_s'])}–{mmss(p['total_s'])}", "fecho (último décimo)",
                   "; ".join(fecho_txt) or "sem dado"))
    return linhas


def dentro_do_bloco(molde: dict) -> list[str]:
    itens = []
    abre = traco(molde, "bloco_abre_com_caso")
    if abre:
        itens.append(f"o bloco abre com caso em {descreve_traco(abre)}")
    antes = traco(molde, "caso_antes_do_conceito")
    if antes:
        itens.append(
            f"há caso antes do conceito em {descreve_traco(antes)}; tempo de caso antes do conceito "
            f"{descreve(medida(molde, 'batidas_caso_antes_conceito_s'), ' s')}"
        )
    titulo = traco(molde, "titulo_dito")
    if titulo:
        itens.append(
            f"o título do bloco é dito na fala nos primeiros 20 s em {descreve_traco(titulo)}; "
            f"título com {descreve(medida(molde, 'titulo_palavras'))} palavras"
        )
    bloco = medida(molde, "capitulo_min")
    if bloco:
        itens.append(f"bloco do molde: {descreve(bloco, ' min')}")
    return itens


def _valor(c: dict, chave: str, d: int) -> float | None:
    serie = c.get(chave) or []
    return serie[d] if d < len(serie) else None


def _linha_da_curva(c: dict, d: int, dur: float) -> list[str]:
    def contagem(chave: str) -> str:
        v = _valor(c, chave, d)
        return f"{v * dur / 600:.1f}" if v is not None else "-"

    cortes = _valor(c, "cortes_min", d)
    palavras = _valor(c, "palavras_min", d)
    return [
        f"{mmss(d * dur)}–{mmss((d + 1) * dur)}",
        contagem("voce_por_10min"), contagem("eu_por_10min"), contagem("fonte_por_10min"),
        f"{cortes:.1f}" if cortes is not None else "-",
        f"{palavras:.0f}" if palavras is not None else "-",
    ]


def curvas(molde: dict, p: dict) -> list[list[str]]:
    c = molde.get("curvas", {})
    decimos = int(c.get("decimos", 10))
    dur = p["total_s"] / decimos
    return [_linha_da_curva(c, d, dur) for d in range(decimos)]


ALVOS = (
    ("batidas_pct_caso", "% do tempo em caso"),
    ("batidas_pct_conceito", "% em conceito"),
    ("batidas_pct_voce", "% falando com quem assiste (aplica + pergunta)"),
    ("batidas_pct_narrador", "% do narrador (confissão + opinião)"),
    ("batidas_confissoes", "confissões"),
    ("batidas_ganchos_pagos", "ganchos pagos"),
    ("batidas_chamadas", "chamadas"),
    ("palavras_min", "palavras por minuto"),
    ("cortes_min", "cortes por minuto"),
    ("voce_por_mil", '"você" por mil palavras'),
    ("eu_por_mil", '"eu" por mil palavras'),
    ("fonte_por_mil", "fonte citada na fala, por mil palavras"),
)


def render(molde: dict, duracao_min: float, assunto: str | None, titulo: str, origem: str,
           blocos_pedidos: int | None = None) -> str:
    p = plano(molde, duracao_min, blocos_pedidos)
    v = molde.get("videos", {})
    grupos = ", ".join(molde.get("grupos") or []) or "todos os grupos"
    cab = [
        f"# Partitura: {titulo}",
        "",
        f"Duração-alvo {duracao_min:g} min" + (f", assunto `{assunto}`" if assunto else "") + ".",
        f"Molde: `{origem}`, gerado em {molde.get('gerado_em', '?')}, {v.get('n', '?')} vídeo(s) de "
        f"{grupos}, {v.get('com_batidas', 0)} com batidas"
        + (f", assunto do molde `{molde['assunto']}`" if molde.get("assunto") else "") + ".",
        "",
        "Forma, nunca fato (ADR 031): nenhuma frase, número ou imagem dos vídeos medidos entra no roteiro;"
        " fato só das fichas. `padrao` = 8 ou mais vídeos e 80% ou mais; `indicio` = o resto. Escala: marcos"
        " iniciais absolutos, abertura e blocos proporcionais, blocos do tamanho do molde.",
        "",
        "## Linha do tempo",
        "",
        "| tempo | casa | o molde diz |",
        "|---|---|---|",
    ]
    cab += [f"| {t} | {c} | {d} |" for t, c, d in linha_do_tempo(molde, p)]
    cab += ["", "## Dentro de cada bloco", ""]
    cab += [f"- {item}" for item in dentro_do_bloco(molde)] or ["- sem batidas no molde"]
    cab += [
        "",
        f"## Curvas por décimo (cada décimo = {mmss(p['total_s'] / 10)})",
        "",
        "Contagens já no tamanho deste décimo; cortes e palavras por minuto.",
        "",
        '| décimo | "você" | "eu" | fonte dita | cortes/min | palavras/min |',
        "|---|---|---|---|---|---|",
    ]
    cab += ["| " + " | ".join(linha) + " |" for linha in curvas(molde, p)]
    cab += [
        "",
        "## Alvos para medir o rascunho",
        "",
        "Depois do roteiro: batidas cegas do nosso episódio (`batidas.md`) e `narrativa.py medir`; "
        "ritmo e vocabulário por `medir.py`. Dentro de q1–q3 está no molde.",
        "",
        "| medida | q1 | mediana | q3 | n |",
        "|---|---|---|---|---|",
    ]
    for chave, nome in ALVOS:
        item = medida(molde, chave)
        if item:
            q1, q3 = item.get("q1", "-"), item.get("q3", "-")
            cab.append(f"| {nome} | {q1} | {item['mediana']} | {q3} | {item['n']} |")
    cab.append("")
    return "\n".join(cab)


def gravar(caminho: Path, texto: str, sobrescrever: bool) -> None:
    if caminho.exists() and not sobrescrever:
        raise FileExistsError(f"{caminho} já existe; use --sobrescrever")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("molde", type=Path)
    parser.add_argument("--duracao", type=float, required=True, help="duração-alvo em minutos")
    parser.add_argument("--assunto", choices=ASSUNTOS)
    parser.add_argument("--blocos", type=int, help="número de blocos, se quiser fixar")
    parser.add_argument("--titulo", default="")
    parser.add_argument(
        "--episodio", type=Path, help="pasta data/episodes/<id>: grava partitura.md e molde.json",
    )
    parser.add_argument("--saida", type=Path, help="arquivo .md (sem --episodio); padrão: stdout")
    parser.add_argument("--sobrescrever", action="store_true")
    args = parser.parse_args(argv)

    molde = json.loads(args.molde.read_text(encoding="utf-8"))
    if args.assunto and molde.get("assunto") and molde["assunto"] != args.assunto:
        print(
            f"aviso: o molde é do assunto {molde['assunto']!r}; a partitura pede {args.assunto!r}",
            file=sys.stderr,
        )
    titulo = args.titulo or (args.episodio.name if args.episodio else "episódio")
    texto = render(molde, args.duracao, args.assunto, titulo, str(args.molde), args.blocos)
    try:
        if args.episodio:
            copia = dict(molde)
            copia["copiado_em"] = date.today().isoformat()
            copia["copiado_de"] = str(args.molde)
            gravar(args.episodio / "molde.json", json.dumps(copia, ensure_ascii=False, indent=2) + "\n",
                   args.sobrescrever)
            gravar(args.episodio / "partitura.md", texto, args.sobrescrever)
            print(f"partitura e molde em {args.episodio}")
        elif args.saida:
            gravar(args.saida, texto, args.sobrescrever)
            print(f"partitura em {args.saida}")
        else:
            print(texto)
    except FileExistsError as erro:
        print(erro, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
