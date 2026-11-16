"""Monta as pastas de episódio dos três Reels de consistent hashing (texto e conferência; sem voz nem render).

Uso: python3 montar_episodios_reels.py   (reescreve data/episodes/reel-consistent-hashing-<empresa>-pt/)
Escreve narracao.json, content.json (cópia de reels/<empresa>/content.pt.json),
voice/glossary.json e medicao.json.
Falas: reels-por-empresa.md (aprovadas pelo dono em 2026-11-08; Amazon e Akamai sem `turn`
para manter 60% neutras).
"""

import json
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
RES = "renders/short-consistent-hashing-java/demo/resultado.txt"
AMB = (
    "Java 25.0.4.1, AMD Ryzen 7 5700U, 100 mil ids de sessão (semente 42), MD5 (4 primeiros bytes), "
    "servidores 4 → 5, "
    "anel em TreeMap, 15 rodadas com sonda de CPU abaixo de 0,12 s, 2026-11-08; só em memória, sem rede nem "
    "cache real"
)

L_MOD = "modo=modulo pontos=0 chaves=100000 clusters=1 movidas_pct=80.18"
L_A1 = "modo=anel pontos=1 chaves=100000 clusters=20 movidas_pct=23.31"
L_A10 = "modo=anel pontos=10 chaves=100000 clusters=20 movidas_pct=18.33"
L_A100 = "modo=anel pontos=100 chaves=100000 clusters=20 movidas_pct=20.13"
L_C1 = ("modo=anel pontos=1 chaves=100000 clusters=20 movidas_pct=23.31 movidas_pct_min=0.70 "
    "movidas_pct_max=71.33 fora_do_novo=0 desvio_pct=87.00 desvio_pct_max=141.34 carga_max_pct_do_ideal=251.5"
)
L_C10 = ("modo=anel pontos=10 chaves=100000 clusters=20 movidas_pct=18.33 movidas_pct_min=9.95 "
    "movidas_pct_max=33.63 fora_do_novo=0 desvio_pct=27.16 desvio_pct_max=45.79 carga_max_pct_do_ideal=140.2"
)
L_C100 = ("modo=anel pontos=100 chaves=100000 clusters=20 movidas_pct=20.13 movidas_pct_min=17.66 "
    "movidas_pct_max=23.77 fora_do_novo=0 desvio_pct=8.19 desvio_pct_max=14.33 carga_max_pct_do_ideal=111.2"
)
L_SRV = "servidores 4 -> 5"


def n(valor, trechos, medidos, cenas, tol=0, nota=None):
    d = {"valor": valor, "trechos": trechos, "medidos": medidos, "tolerancia": tol, "cenas": cenas}
    if nota:
        d["nota"] = nota
    return d


def externo(valor, cenas, nota):
    return {"valor": valor, "trechos": [], "medidos": [], "tolerancia": 0, "cenas": cenas, "nota": nota}


def comuns(cena_versus: str, extra_100: tuple = ()) -> list:
    return [
        n(
            80,
            [L_MOD],
            [80.18],
            [cena_versus],
            0.01,
            "'oitenta por cento': arredondado de 80,18% (módulo, 4 → 5 servidores)",
        ),
        n(
            20,
            [L_A100],
            [20.13],
            [cena_versus],
            0.01,
            "'vinte por cento': arredondado de 20,13% (anel, 100 pontos por servidor)",
        ),
        n(
            100,
            [L_A100],
            [100],
            [cena_versus, "pontos", *extra_100],
            0,
            "cem pontos por servidor (parâmetro da medição); em 'por cento' o detector lê 'cento' como 100",
        ),
        n(4, [L_SRV], [4], [cena_versus], 0, "'4 → 5' servidores: a medição passa de quatro para cinco"),
        n(5, [L_SRV], [5], [cena_versus], 0, "'4 → 5' servidores: a medição passa de quatro para cinco"),
    ]


def amazon() -> dict:
    nums = comuns("medicao") + [
        n(1, [L_A1], [1], ["pontos"], 0, "rótulo 'Anel, 1 ponto' da barra"),
        n(10, [L_A10], [10], ["pontos"], 0, "rótulo 'Anel, 10 pontos' da barra"),
        n(251.5, [L_C1], [251.5], ["pontos"], 0, "carga do servidor mais cheio com 1 ponto, em % da ideal"),
        n(
            140.2,
            [L_C10],
            [140.2],
            ["pontos"],
            0,
            "carga do servidor mais cheio com 10 pontos, em % da ideal",
        ),
        n(
            111.2,
            [L_C100],
            [111.2],
            ["pontos"],
            0,
            "carga do servidor mais cheio com 100 pontos, em % da ideal",
        ),
    ]
    return {"arquivo": RES, "ambiente": AMB, "numeros": nums}


def akamai() -> dict:
    nums = comuns("servidor-novo", ("fecho",)) + [
        n(80, [L_MOD], [80.18], ["fecho"], 0.01, "'80%' do cache no fecho: arredondado de 80,18% (módulo)"),
    ]
    return {"arquivo": RES, "ambiente": AMB, "numeros": nums}


def discord() -> dict:
    nota = ("Número do post do Discord (F-Di2, F-Di4 em fontes.md), não da medição do dono; dito e mostrado "
        "como deles."
    )
    nums = [
        externo(2017, ["anel"], "Ano do post do Discord (06/07/2017), F-Di1; fonte externa."),
        externo(12, ["solucao"], nota + " 12 µs por consulta ao processo do anel."),
        externo(
            0.3,
            ["solucao"],
            nota + " 0,3 µs na tela (título e seta da cena): consulta com o anel em memória compartilhada.",
        ),
        externo(
            0,
            ["solucao"],
            nota + " 'zero vírgula três': o 0 de 0,3 µs (consulta com o anel em memória compartilhada).",
        ),
        externo(
            3,
            ["solucao"],
            nota + " 'zero vírgula três': o 3 de 0,3 µs (consulta com o anel em memória compartilhada).",
        ),
    ]
    return {
        "arquivo": RES,
        "ambiente": "Números do Discord Engineering (06/07/2017), medidos por eles na produção deles; nada "
            "medido aqui. "
        "A medição do dono (resultado.txt) não é usada neste Reel.",
        "numeros": nums,
    }


NARRACAO = {
    "amazon": [
        ("pergunta", "Como a Amazon adiciona um servidor sem esvaziar o cache?", "hook"),
        (
            "anel",
            "No Dynamo, chaves e servidores ficam num anel, e cada chave vai para o primeiro servidor no "
            "sentido horário, e quando um servidor entra, só os vizinhos sentem a mudança.",
            None,
        ),
        (
            "medicao",
            "Na minha medição, o resto do hash mexeu em oitenta por cento das chaves, e o anel com cem "
            "pontos por servidor, em vinte.",
            None,
        ),
        (
            "pontos",
            "Com um ponto só a carga fica torta, e por isso o Dynamo usa vários pontos por servidor, os nós "
            "virtuais.",
            None,
        ),
        ("fecho", "Quantos pontos virtuais você daria para cada servidor?", "invite"),
    ],
    "akamai": [
        ("pergunta", "Como a Akamai decide qual servidor entrega cada arquivo?", "hook"),
        (
            "circulo",
            "Arquivos e servidores vão para o mesmo círculo, e cada arquivo fica com o próximo servidor no "
            "sentido horário.",
            None,
        ),
        (
            "origem",
            "Esse método foi a primeira inovação algorítmica da rede de entrega da Akamai, e ele divide a "
            "carga dentro de um cluster.",
            None,
        ),
        (
            "servidor-novo",
            "Quando entra um servidor, só os arquivos que caem nele precisam mudar, e na minha medição, com "
            "cem pontos por servidor, foram vinte por cento, contra oitenta no resto do hash.",
            None,
        ),
        ("fecho", "O seu sistema aguenta mover oitenta por cento do cache de uma vez?", "invite"),
    ],
    "discord": [
        ("pergunta", "Como o Discord descobre em qual nó está cada comunidade?", "hook"),
        (
            "anel",
            "Em dois mil e dezessete, eles usavam um anel de consistent hashing para achar o nó de cada "
            "comunidade.",
            None,
        ),
        (
            "gargalo",
            "Mas quando muitos usuários reconectavam juntos, o processo dono do anel não dava conta e o "
            "sistema sobrecarregava.",
            None,
        ),
        (
            "solucao",
            "A saída foi pôr o anel numa memória compartilhada só de leitura, e cada consulta caiu de doze "
            "microssegundos para zero vírgula três.",
            None,
        ),
        ("fecho", "O seu anel fica na memória de quem consulta, ou atrás de um processo só?", "invite"),
    ],
}
# Pronúncias são hipóteses a conferir na escuta (a voz clonada decide);
# termos por palavra inteira (ADR 009, glossário).
GLOSSARIO = [
    ("hash", "ráche"),
    ("hashing", "ráchin"),
    ("consistent", "consístent"),
    ("Dynamo", "dínamo"),
    ("Akamai", "ákamai"),
    ("Discord", "discórd"),
    ("TreeMap", "trí mép"),
    ("cluster", "clâster"),
]
MEDICAO = {"amazon": amazon, "akamai": akamai, "discord": discord}

if __name__ == "__main__":
    for emp in ("amazon", "discord", "akamai"):
        pasta = RAIZ / "data" / "episodes" / f"reel-consistent-hashing-{emp}-pt"
        (pasta / "voice").mkdir(parents=True, exist_ok=True)
        linhas = []
        for cena, texto, entrega in NARRACAO[emp]:
            d = {"scene": cena, "text": texto}
            if entrega:
                d["delivery"] = entrega
            linhas.append(d)
        (pasta / "narracao.json").write_text(
            json.dumps({"language": "pt-BR", "lines": linhas}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        shutil.copyfile(AQUI / "reels" / emp / "content.pt.json", pasta / "content.json")
        (pasta / "voice" / "glossary.json").write_text(
            json.dumps(
                {"termos": [{"escrita": e, "fala": f} for e, f in GLOSSARIO]}, ensure_ascii=False, indent=2
            )
            + "\n",
            encoding="utf-8",
        )
        (pasta / "medicao.json").write_text(
            json.dumps(MEDICAO[emp](), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(pasta)
