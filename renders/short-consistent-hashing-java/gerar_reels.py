"""Gera os content.pt.json dos três Reels de consistent hashing (Amazon, Discord, Akamai).

Uso: python3 gerar_reels.py   (reescreve reels/<empresa>/content.pt.json; as animações Lottie são as do Short)
Texto e origem de cada número: reels-por-empresa.md e fontes.md.
Durações são do plano; o `tempos` ajusta pela voz.
"""

import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
AMBIENTE = "Java 25 · Ryzen 7 5700U · 100 mil sessões · 4 → 5 servidores · 15 rodadas · só em memória"


def base(footer: str, assets: dict) -> dict:
    return {
        "version": 2,
        "locale": "pt-BR",
        "format": "vertical",
        "fps": 30,
        "style": "editorial",
        "safeArea": "shorts",
        "cover": True,
        "footer": footer,
        "assets": assets,
        "scenes": [],
    }


ANEL = {"anel": {"kind": "lottie", "path": "lottie/anel.json"}}


def hook(texto: str, destaque: str, kicker: str, dur: float = 3.0) -> dict:
    return {
        "id": "pergunta",
        "type": "hook",
        "durationSec": dur,
        "kicker": kicker,
        "text": texto,
        "highlight": destaque,
    }


def versus(id_: str, dur: float, vence: float) -> dict:
    return {
        "id": id_,
        "type": "versus",
        "durationSec": dur,
        "title": "Quem trocou de servidor? (4 → 5)",
        "left": {"title": "Módulo (hash % N)", "value": "80,18%", "lines": ["das sessões trocaram"]},
        "right": {"title": "Anel, 100 pontos", "value": "20,13%", "lines": ["trocaram, todas para o novo"]},
        "winner": "right",
        "winnerAtSec": vence,
    }


def fecho(texto: str, sub: str, dur: float = 3.8) -> dict:
    return {
        "id": "fecho",
        "type": "end_card",
        "durationSec": dur,
        "variant": "follow",
        "text": texto,
        "sub": sub,
    }


def pontos() -> dict:
    return {
        "id": "pontos",
        "type": "categories",
        "durationSec": 8.0,
        "title": "Carga do servidor mais cheio, em % da ideal",
        "unit": "%",
        "decimals": 1,
        "highlight": "Anel, 100 pontos",
        "items": [
            {"label": "Anel, 1 ponto", "value": 251.5},
            {"label": "Anel, 10 pontos", "value": 140.2},
            {"label": "Anel, 100 pontos", "value": 111.2},
        ],
    }


def amazon() -> dict:
    c = base(
        "Amazon Dynamo (SOSP 2007) · medição de 08/11/2026 · Java 25 · 100 mil sessões · 4 → 5 servidores · "
        "15 rodadas",
        ANEL,
    )
    c["scenes"] = [
        hook(
            "Como a Amazon adiciona um servidor sem esvaziar o cache?",
            "sem esvaziar o cache",
            "Amazon · Dynamo",
        ),
        {"id": "anel", "type": "animation", "durationSec": 13.0, "assetId": "anel", "colors": "original"},
        versus("medicao", 10.0, 4.0),
        pontos(),
        fecho("Quantos pontos virtuais por servidor?", "Comenta o seu número"),
    ]
    return c


def akamai() -> dict:
    c = base(
        "Maggs e Sitaraman (ACM CCR, 2015) · medição de 08/11/2026 · Java 25 · 100 mil sessões · 4 → 5 "
        "servidores",
        ANEL,
    )
    c["scenes"] = [
        hook("Como a Akamai decide qual servidor entrega cada arquivo?", "qual servidor", "Akamai · CDN"),
        {"id": "circulo", "type": "animation", "durationSec": 9.0, "assetId": "anel", "colors": "original"},
        {
            "id": "origem",
            "type": "flow",
            "durationSec": 8.5,
            "title": "Dentro de um cluster da Akamai",
            "legend": False,
            "nodes": [
                {"id": "pedido", "label": "Pedido do arquivo", "x": 0.5, "y": 0.0},
                {"id": "cluster", "label": "Escolhe o cluster", "x": 0.5, "y": 0.27},
                {
                    "id": "hash",
                    "label": "Hash consistente",
                    "sublabel": "escolhe o servidor",
                    "x": 0.5,
                    "y": 0.54,
                },
                {"id": "servidor", "label": "Servidor de borda", "x": 0.5, "y": 0.8},
            ],
            "edges": [
                {"from": "pedido", "to": "cluster", "kind": "scheduling"},
                {"from": "cluster", "to": "hash", "kind": "scheduling"},
                {"from": "hash", "to": "servidor", "kind": "scheduling"},
            ],
            "states": [
                {"node": "pedido", "atSec": 1.2, "state": "running"},
                {"node": "pedido", "atSec": 2.2, "state": "done"},
                {"node": "cluster", "atSec": 2.2, "state": "running"},
                {"node": "cluster", "atSec": 3.4, "state": "done"},
                {"node": "hash", "atSec": 3.4, "state": "running"},
                {"node": "hash", "atSec": 5.6, "state": "done"},
                {"node": "servidor", "atSec": 5.6, "state": "running"},
                {"node": "servidor", "atSec": 6.6, "state": "done"},
            ],
        },
        versus("servidor-novo", 12.5, 6.0),
        fecho("Aguenta mover 80% do cache?", "Comenta o que você faria"),
    ]
    return c


def discord() -> dict:
    c = base("Discord Engineering (06/07/2017) · números do Discord, não medidos aqui", {})
    c["scenes"] = [
        hook("Como o Discord descobre em qual nó está cada comunidade?", "qual nó", "Discord · 2017"),
        {
            "id": "anel",
            "type": "flow",
            "durationSec": 8.0,
            "title": "Achar o nó da comunidade",
            "legend": False,
            "nodes": [
                {"id": "sessao", "label": "Sessão", "sublabel": "quer a comunidade", "x": 0.5, "y": 0.0},
                {"id": "anel", "label": "Anel de hash", "sublabel": "consistent hashing", "x": 0.5, "y": 0.4},
                {"id": "no", "label": "Nó da comunidade", "x": 0.5, "y": 0.8},
            ],
            "edges": [
                {"from": "sessao", "to": "anel", "kind": "data", "label": "consulta"},
                {"from": "anel", "to": "no", "kind": "data", "label": "devolve o nó"},
            ],
            "states": [
                {"node": "sessao", "atSec": 1.2, "state": "running"},
                {"node": "sessao", "atSec": 2.4, "state": "done"},
                {"node": "anel", "atSec": 2.4, "state": "running"},
                {"node": "anel", "atSec": 4.2, "state": "done"},
                {"node": "no", "atSec": 4.2, "state": "running"},
                {"node": "no", "atSec": 5.6, "state": "done"},
            ],
            "tokens": [
                {"id": "q", "from": "sessao", "to": "anel", "atSec": 1.4, "durationSec": 0.9},
                {"id": "r", "from": "anel", "to": "no", "atSec": 4.3, "durationSec": 0.9},
            ],
        },
        {
            "id": "gargalo",
            "type": "flow",
            "durationSec": 8.5,
            "title": "Muitos reconectando de uma vez",
            "legend": False,
            "nodes": [
                {
                    "id": "usuarios",
                    "label": "Usuários",
                    "sublabel": "reconectando juntos",
                    "x": 0.5,
                    "y": 0.0,
                },
                {"id": "processo", "label": "Processo do anel", "sublabel": "um só", "x": 0.5, "y": 0.4},
                {"id": "sistema", "label": "Sistema", "x": 0.5, "y": 0.8},
            ],
            "edges": [
                {"from": "usuarios", "to": "processo", "kind": "data", "label": "consultas"},
                {"from": "processo", "to": "sistema", "kind": "data", "label": "espera"},
            ],
            "states": [
                {"node": "usuarios", "atSec": 1.2, "state": "running"},
                {"node": "processo", "atSec": 2.6, "state": "running"},
                {"node": "processo", "atSec": 5.0, "state": "failed"},
                {"node": "sistema", "atSec": 6.0, "state": "failed"},
            ],
            "tokens": [
                {"id": "c1", "from": "usuarios", "to": "processo", "atSec": 1.4, "durationSec": 0.8},
                {"id": "c2", "from": "usuarios", "to": "processo", "atSec": 1.8, "durationSec": 0.8},
                {"id": "c3", "from": "usuarios", "to": "processo", "atSec": 2.2, "durationSec": 0.8},
                {"id": "c4", "from": "usuarios", "to": "processo", "atSec": 2.6, "durationSec": 0.8},
            ],
        },
        {
            "id": "solucao",
            "type": "flow",
            "durationSec": 10.0,
            "title": "Anel em memória compartilhada: 12 µs → 0,3 µs",
            "legend": False,
            "nodes": [
                {"id": "sessoes", "label": "Sessões", "sublabel": "leem direto", "x": 0.5, "y": 0.0},
                {"id": "anelmem", "label": "Anel", "sublabel": "memória só de leitura", "x": 0.5, "y": 0.74},
            ],
            "edges": [{"from": "sessoes", "to": "anelmem", "kind": "data", "label": "0,3 µs"}],
            "states": [
                {"node": "anelmem", "atSec": 1.4, "state": "running"},
                {"node": "sessoes", "atSec": 4.6, "state": "done"},
            ],
            "tokens": [
                {"id": "l1", "from": "sessoes", "to": "anelmem", "atSec": 2.2, "durationSec": 0.7},
                {"id": "l2", "from": "sessoes", "to": "anelmem", "atSec": 3.2, "durationSec": 0.7},
                {"id": "l3", "from": "sessoes", "to": "anelmem", "atSec": 4.0, "durationSec": 0.7},
            ],
        },
        fecho("Seu anel está na memória de quem consulta?", "Comenta como você faz"),
    ]
    return c


if __name__ == "__main__":
    for nome, fn in (("amazon", amazon), ("discord", discord), ("akamai", akamai)):
        d = AQUI / "reels" / nome
        d.mkdir(parents=True, exist_ok=True)
        link = d / "public"
        if not link.exists():
            link.symlink_to("../../public")
        (d / "content.pt.json").write_text(
            json.dumps(fn(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(d / "content.pt.json")
