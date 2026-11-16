"""Série Kafka: gera content.json, narracao.json e as animações do celular de cada episódio (pt).

Uso: uv run --no-sync python renders/serie-kafka/gerar.py [ep1 ...]
Escreve a pasta de produção em data/episodes/<id>/ (fora do Git) e a cópia versionável
em renders/serie-kafka/<id>/.
As durações são do rascunho; `vp short tempos` estica cada cena até a fala caber. Nada aqui é medição.
Fontes por cena: cenarios.md e fontes.md desta pasta.
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lottie_celular as cel  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
FOOTER = "Fonte: documentação do Apache Kafka 4.4 · app e serviços fictícios"
SERVICOS = [
    ("pagamento", "Pagamento"),
    ("restaurante", "Restaurante"),
    ("entregador", "Entregador"),
    ("notificacao", "Notificação"),
]


def base(assets):
    return {
        "version": 2,
        "locale": "pt-BR",
        "format": "vertical",
        "fps": 30,
        "style": "editorial",
        "safeArea": "shorts",
        "cover": True,
        "footer": FOOTER,
        "assets": {name: {"kind": "lottie", "path": f"lottie/{name}.json"} for name in assets},
    }


def celular_abertura():
    s = cel.Scene(7.4, 6.9, "celular-abertura")
    cel.phone(s, "App de delivery · Kafka")
    cel.notification(s, 0, "Pagamento aprovado", "Seu pedido foi pago", "check", cel.GREEN, 0)
    cel.notification(s, 1, "Restaurante aceitou", "Preparando seu pedido", "check", cel.GOLD, 2.0)
    cel.notification(
        s, 2, "Procurando entregador", "Aguarde um instante", "spinner", cel.BLUE, 3.4, alert_at=6.0
    )
    s.text(
        "o pedido parou",
        cel.W / 2,
        cel.SLOT_TOP + 3 * cel.SLOT_GAP - 10,
        46,
        cel.CORAL,
        6.6,
        s.seconds,
        justify=2,
    )
    return s


def celular_volta():
    s = cel.Scene(4.0, 3.3, "celular-volta")
    cel.phone(s, "Do lado do cliente")
    cel.notification(s, 0, "Pagamento aprovado", "Seu pedido foi pago", "check", cel.GREEN, 0)
    cel.notification(s, 1, "Restaurante aceitou", "Preparando seu pedido", "check", cel.GOLD, 0.5)
    cel.notification(s, 2, "Pedido pronto", "Aguardando o entregador", "check", cel.VIOLET, 1.2)
    cel.notification(s, 3, "Entregador a caminho", "Chega em instantes", "bike", cel.BLUE, 2.4)
    return s


def nos_kafka():
    return [
        {"id": "pedidos", "label": "Pedidos", "column": 0, "lane": 0},
        {"id": "topico", "label": "Tópico pedidos", "sublabel": "Kafka", "column": 0, "lane": 2},
        *[{"id": i, "label": n, "column": 1, "lane": k} for k, (i, n) in enumerate(SERVICOS)],
    ]


def arestas_kafka():
    return [
        {"from": "pedidos", "to": "topico", "label": "escreve"},
        *[{"from": "topico", "to": i} for i, _ in SERVICOS],
    ]


def ep1():
    content = base(["celular-abertura", "celular-volta"])
    content["scenes"] = [
        {
            "id": "abertura",
            "type": "animation",
            "durationSec": 7.6,
            "assetId": "celular-abertura",
            "colors": "original",
        },
        {
            "id": "direto",
            "type": "flow",
            "durationSec": 6.6,
            "title": "Chamada direta, um por um",
            "legend": False,
            "nodes": [
                {"id": "pedidos", "label": "Pedidos", "column": 0, "lane": 1},
                *[{"id": i, "label": n, "column": 1, "lane": k} for k, (i, n) in enumerate(SERVICOS)],
            ],
            "edges": [{"from": "pedidos", "to": i} for i, _ in SERVICOS],
            "direction": "right",
            "states": [
                {"node": "pedidos", "atSec": 1.4, "state": "running"},
                {"node": "pagamento", "atSec": 2.0, "state": "running"},
                {"node": "restaurante", "atSec": 3.3, "state": "running"},
                {"node": "entregador", "atSec": 4.6, "state": "failed"},
                {"node": "pedidos", "atSec": 4.7, "state": "waiting"},
            ],
            "tokens": [
                {"id": "c1", "from": "pedidos", "to": "pagamento", "atSec": 1.4, "durationSec": 0.6},
                {"id": "r1", "from": "pagamento", "to": "pedidos", "atSec": 2.1, "durationSec": 0.5},
                {"id": "c2", "from": "pedidos", "to": "restaurante", "atSec": 2.7, "durationSec": 0.6},
                {"id": "r2", "from": "restaurante", "to": "pedidos", "atSec": 3.4, "durationSec": 0.5},
                {"id": "c3", "from": "pedidos", "to": "entregador", "atSec": 4.0, "durationSec": 0.6},
            ],
        },
        {
            "id": "topico",
            "type": "flow",
            "durationSec": 7.0,
            "title": "Com Kafka: escreve uma vez",
            "legend": False,
            "nodes": nos_kafka(),
            "edges": arestas_kafka(),
            "direction": "right",
            "states": [
                {"node": "pedidos", "atSec": 1.4, "state": "running"},
                {"node": "pedidos", "atSec": 2.2, "state": "idle"},
                {"node": "pagamento", "atSec": 3.0, "state": "running"},
                {"node": "restaurante", "atSec": 3.5, "state": "running"},
                {"node": "notificacao", "atSec": 3.9, "state": "running"},
                {"node": "entregador", "atSec": 4.6, "state": "running"},
            ],
            "tokens": [
                {
                    "id": "e1",
                    "from": "pedidos",
                    "to": "topico",
                    "atSec": 1.4,
                    "durationSec": 0.7,
                    "label": "pedido #123",
                },
                {"id": "l1", "from": "topico", "to": "pagamento", "atSec": 2.4, "durationSec": 0.6},
                {"id": "l2", "from": "topico", "to": "restaurante", "atSec": 2.9, "durationSec": 0.6},
                {"id": "l3", "from": "topico", "to": "notificacao", "atSec": 3.3, "durationSec": 0.6},
                {"id": "l4", "from": "topico", "to": "entregador", "atSec": 4.0, "durationSec": 0.6},
            ],
        },
        {
            "id": "codigo",
            "type": "code",
            "durationSec": 4.4,
            "title": "Em Java, o produtor",
            "lines": [
                "var evento = new ProducerRecord<>(",
                '    "pedidos", id, json);',
                "producer.send(evento);",
            ],
            "highlight": [{"token": '"pedidos"'}, {"token": "send"}],
            "steps": [
                {"atSec": 0.4, "lines": [1, 2], "note": "O evento vai para o tópico pedidos"},
                {"atSec": 1.8, "lines": [3, 3], "note": "Não espera nenhum consumidor"},
            ],
        },
        {
            "id": "falha",
            "type": "flow",
            "durationSec": 6.6,
            "title": "O Entregador caiu: o evento espera",
            "legend": False,
            "nodes": nos_kafka(),
            "edges": arestas_kafka(),
            "direction": "right",
            "states": [
                {"node": "entregador", "atSec": 1.3, "state": "failed"},
                {"node": "pagamento", "atSec": 2.8, "state": "running"},
                {"node": "restaurante", "atSec": 3.2, "state": "running"},
                {"node": "notificacao", "atSec": 3.6, "state": "running"},
                {"node": "entregador", "atSec": 4.1, "state": "running"},
            ],
            "tokens": [
                {
                    "id": "e2",
                    "from": "pedidos",
                    "to": "topico",
                    "atSec": 1.4,
                    "durationSec": 0.7,
                    "label": "pedido #124",
                },
                {"id": "m1", "from": "topico", "to": "pagamento", "atSec": 2.2, "durationSec": 0.6},
                {"id": "m2", "from": "topico", "to": "restaurante", "atSec": 2.6, "durationSec": 0.6},
                {"id": "m3", "from": "topico", "to": "notificacao", "atSec": 3.0, "durationSec": 0.6},
                {
                    "id": "m4",
                    "from": "topico",
                    "to": "entregador",
                    "atSec": 4.3,
                    "durationSec": 0.7,
                    "label": "volta e lê",
                },
            ],
        },
        {
            "id": "cliente",
            "type": "animation",
            "durationSec": 4.4,
            "assetId": "celular-volta",
            "colors": "original",
        },
        {
            "id": "decisao",
            "type": "versus",
            "durationSec": 5.0,
            "title": "O que muda no desenho",
            "left": {
                "title": "Chamada direta",
                "lines": ["simples de começar", "um serviço caído trava o resto"],
            },
            "right": {
                "title": "Tópico no Kafka",
                "lines": ["serviços desacoplados", "um cluster a mais para operar"],
            },
        },
        {
            "id": "fecho",
            "type": "end_card",
            "durationSec": 3.4,
            "variant": "next",
            "text": "Direto ou por um tópico?",
            "sub": "Parte 2: por que a mensagem não some",
            "series": {"text": "Kafka", "part": 1, "total": 4},
        },
    ]
    narration = {
        "language": "pt-BR",
        "lines": [
            {
                "scene": "abertura",
                "text": "Meio-dia no app de delivery. Cada passo do pedido vira um aviso no celular. "
                "Até que um serviço cai, e tudo para.",
                "delivery": "hook",
            },
            {
                "scene": "direto",
                "text": "O serviço de pedidos chama um por vez e espera. "
                "Se o Entregador cai, ele fica preso.",
            },
            {
                "scene": "topico",
                "text": "Com Kafka, ele escreve o evento uma vez num tópico e segue. "
                "Cada serviço lê no seu ritmo.",
                "delivery": "turn",
            },
            {
                "scene": "codigo",
                "text": "Em Java, é um send no tópico pedidos, e o serviço segue sem esperar ninguém.",
            },
            {
                "scene": "falha",
                "text": "Se o Entregador cai, o evento fica guardado no tópico, e ele lê quando voltar.",
                "delivery": "calm",
            },
            {"scene": "cliente", "text": "E o cliente continua recebendo os avisos."},
            {
                "scene": "decisao",
                "text": "O ganho é desacoplar. O custo é um cluster para operar, ou um serviço gerenciado.",
            },
            {
                "scene": "fecho",
                "text": "Você ligaria seus serviços direto, ou por um tópico?",
                "delivery": "invite",
            },
        ],
    }
    return "short-kafka-por-que-existe-pt", content, narration, [celular_abertura(), celular_volta()]


def episodes():
    """ep1 aqui; os outros em epN.py desta pasta, cada um com uma função episode()."""
    found = {"ep1": ep1}
    for module in sorted(BASE.glob("ep[0-9].py")):
        found[module.stem] = __import__(module.stem).episode
    return found


def write(episode_id, content, narration, animations):
    production = ROOT / "data/episodes" / episode_id
    versioned = BASE / episode_id
    (production / "public/lottie").mkdir(parents=True, exist_ok=True)
    (versioned / "lottie").mkdir(parents=True, exist_ok=True)
    licencas = {}
    for anim in animations:
        data = anim.finish()
        for folder in (production / "public/lottie", versioned / "lottie"):
            (folder / f"{anim.name}.json").write_text(data, encoding="utf-8")
        licencas[anim.name] = {
            "license": "Original",
            "author": "projeto (gerado por renders/serie-kafka/gerar.py)",
            "sha256": hashlib.sha256(data.encode()).hexdigest(),
            "usage_notes": "Formas geométricas e texto; sem pessoas, marcas ou imagem externa.",
        }
    dump = lambda obj: json.dumps(obj, ensure_ascii=False, indent=2) + "\n"  # noqa: E731
    (production / "content.json").write_text(dump(content), encoding="utf-8")
    (production / "narracao.json").write_text(dump(narration), encoding="utf-8")
    (versioned / "content.pt.json").write_text(dump(content), encoding="utf-8")
    (versioned / "narracao.pt.json").write_text(dump(narration), encoding="utf-8")
    (versioned / "licencas.json").write_text(dump(licencas), encoding="utf-8")
    words = sum(len(line["text"].split()) for line in narration["lines"])
    print(f"{episode_id}: {len(content['scenes'])} cenas, {words} palavras (~{words / 2.5:.0f} s de fala)")


def main(argv):
    available = episodes()
    for name in argv or list(available):
        write(*available[name]())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
