"""Série Kafka, episódio 3: partição e chave, ordem e escala (pt).

Gerado por `gerar.py ep3`. Fontes por fala e tela: short-kafka-particao-pt/fontes.md. Nada aqui é medição:
pedidos, consumidores e partições são exemplos didáticos.
"""

import gerar
import lottie_celular as cel

EPISODE_ID = "short-kafka-particao-pt"
FOOTER = "Fonte: docs do Apache Kafka 4.4 e do RabbitMQ · app e serviços fictícios"
PARTICOES = [("p0", "Partição 0"), ("p1", "Partição 1"), ("p2", "Partição 2")]
CONSUMIDORES = [
    ("c1", "Consumidor 1"),
    ("c2", "Consumidor 2"),
    ("c3", "Consumidor 3"),
    ("c4", "Consumidor 4"),
]


def celular_ordem_errada():
    """O risco da fila: o 'saiu para entrega' chega antes do 'pagamento aprovado'.

    Tempos presos à fala da abertura (19 palavras a ~2,9 palavras/s, pausa depois de "fila" e de "cliente"):
    "o pedido sai" começa por volta de 4,5 s e "antes de ser pago" por volta de 5,5 s. O cartão do pedido já
    está na tela no quadro 0 (capa). O Lottie para no último quadro se a cena for mais longa.
    """
    s = cel.Scene(7.2, 6.7, "celular-ordem-errada")
    cel.phone(s, "App de delivery · Kafka")
    cel.notification(s, 0, "Pedido #7 criado", "Seu pedido foi registrado", "check", cel.GOLD, 0)
    cel.notification(s, 1, "Saiu para entrega", "O entregador já pegou", "bike", cel.BLUE, 4.5)
    cel.notification(s, 2, "Pagamento aprovado", "Seu pedido foi pago", "check", cel.GREEN, 5.5, alert_at=6.1)
    y = cel.SLOT_TOP + 3 * cel.SLOT_GAP - 10
    s.text("fora de ordem", cel.W / 2, y, 46, cel.CORAL, 6.3, s.seconds, justify=2)
    return s


def celular_ordem_certa():
    s = cel.Scene(3.6, 2.6, "celular-ordem-certa")
    cel.phone(s, "Com a chave pedidoId")
    cel.notification(s, 0, "Pedido #7 criado", "Seu pedido foi registrado", "check", cel.GOLD, 0)
    cel.notification(s, 1, "Pagamento aprovado", "Seu pedido foi pago", "check", cel.GREEN, 0.6)
    cel.notification(s, 2, "Saiu para entrega", "O entregador já pegou", "bike", cel.BLUE, 1.4)
    return s


def no(node_id, label, column, lane, sublabel=None):
    item = {"id": node_id, "label": label, "column": column, "lane": lane}
    if sublabel:
        item["sublabel"] = sublabel
    return item


def ficha(token_id, origem, destino, at, label=None, duration=0.6):
    item = {"id": token_id, "from": origem, "to": destino, "atSec": at, "durationSec": duration}
    if label:
        item["label"] = label
    return item


def cena_fila():
    """Fila comum com 4 consumidores: o '#7 pago' volta (reentrega) e o '#7 saiu' passa na frente.

    Fonte: R-Q P85.
    """
    return {
        "id": "fila",
        "type": "flow",
        "durationSec": 6.2,
        "title": "Fila: a reentrega troca a ordem",
        "legend": False,
        "direction": "right",
        "nodes": [
            no("fila", "Fila", 0, 1, "fila comum"),
            *[no(i, n, 1, k) for k, (i, n) in enumerate(CONSUMIDORES)],
        ],
        "edges": [
            *[{"from": "fila", "to": i} for i, _ in CONSUMIDORES],
            {"from": "c1", "to": "fila", "kind": "completion", "dashed": True},
        ],
        "states": [
            {"node": "c1", "atSec": 2.0, "state": "running"},
            {"node": "c1", "atSec": 2.4, "state": "failed"},
            {"node": "c2", "atSec": 3.5, "state": "running"},
            {"node": "c1", "atSec": 4.6, "state": "running"},
        ],
        "tokens": [
            ficha("t1", "fila", "c1", 1.4, "#7 pago"),
            ficha("t2", "c1", "fila", 2.5, "volta"),
            ficha("t3", "fila", "c2", 2.9, "#7 saiu"),
            ficha("t4", "fila", "c1", 4.0, "#7 pago"),
        ],
    }


def cena_chave():
    """Produtor com a chave pedidoId: a mesma chave cai sempre na mesma partição (K-INT P33)."""
    eventos = [
        ("k1", "p0", "#3 criado"),
        ("k2", "p1", "#7 criado"),
        ("k3", "p2", "#9 criado"),
        ("k4", "p1", "#7 pago"),
        ("k5", "p0", "#3 pago"),
        ("k6", "p1", "#7 saiu"),
    ]
    return {
        "id": "chave",
        "type": "flow",
        "durationSec": 6.0,
        "title": "Mesma chave, mesma partição",
        "legend": False,
        "direction": "right",
        "nodes": [
            no("produtor", "Produtor", 0, 1, "chave pedidoId"),
            *[no(i, n, 1, k) for k, (i, n) in enumerate(PARTICOES)],
        ],
        "edges": [{"from": "produtor", "to": i} for i, _ in PARTICOES],
        "states": [{"node": "p1", "atSec": 2.4, "state": "running"}],
        "tokens": [ficha(t, "produtor", p, 1.4 + 0.4 * k, label) for k, (t, p, label) in enumerate(eventos)],
    }


def cena_ordem():
    """As três partições como raias; na partição 1, o pedido 7 em ordem de escrita (K-INT P33)."""
    return {
        "id": "ordem",
        "type": "lanes",
        "durationSec": 5.0,
        "title": "Na partição, a ordem é a de escrita",
        "lanes": [
            {
                "name": "Part. 0",
                "ops": [
                    {"t": 0.3, "atSec": 1.0, "label": "#3 criado"},
                    {"t": 0.7, "atSec": 2.0, "label": "#3 pago"},
                ],
            },
            {
                "name": "Part. 1",
                "ops": [
                    {"t": 0.2, "atSec": 0.6, "label": "#7 criado", "kind": "commit"},
                    {"t": 0.5, "atSec": 1.4, "label": "#7 pago", "kind": "commit"},
                    {"t": 0.8, "atSec": 2.2, "label": "#7 saiu", "kind": "commit"},
                ],
            },
            {"name": "Part. 2", "ops": [{"t": 0.4, "atSec": 1.2, "label": "#9 criado"}]},
        ],
    }


def cena_grupo():
    """Grupo de consumidores: um consumidor por partição; o 4º fica sem partição.

    Consequência de K-DES P68.
    """
    return {
        "id": "grupo",
        "type": "flow",
        "durationSec": 5.6,
        "title": "Um consumidor por partição",
        "legend": False,
        "direction": "right",
        "nodes": [
            *[no(i, n, 0, k) for k, (i, n) in enumerate(PARTICOES)],
            *[no(i, n, 1, k) for k, (i, n) in enumerate(CONSUMIDORES[:3])],
            no("c4", "Consumidor 4", 1, 3, "sem partição"),
        ],
        "edges": [
            {"from": "p0", "to": "c1"},
            {"from": "p1", "to": "c2"},
            {"from": "p2", "to": "c3"},
        ],
        "states": [
            {"node": "c1", "atSec": 2.0, "state": "running"},
            {"node": "c2", "atSec": 2.3, "state": "running"},
            {"node": "c3", "atSec": 2.6, "state": "running"},
            {"node": "c4", "atSec": 3.0, "state": "idle"},
        ],
        "tokens": [
            ficha("g1", "p0", "c1", 1.4, "#3 pago"),
            ficha("g2", "p1", "c2", 1.7, "#7 pago"),
            ficha("g3", "p2", "c3", 2.0, "#9 criado"),
        ],
    }


def episode():
    content = gerar.base(["celular-ordem-errada", "celular-ordem-certa"])
    content["footer"] = FOOTER
    content["scenes"] = [
        {
            "id": "abertura",
            "type": "animation",
            "durationSec": 7.8,
            "assetId": "celular-ordem-errada",
            "colors": "original",
        },
        cena_fila(),
        cena_chave(),
        cena_ordem(),
        cena_grupo(),
        {
            "id": "codigo",
            "type": "code",
            "durationSec": 4.0,
            "title": "Em Java, a chave do evento",
            "lines": [
                "var evento = new ProducerRecord<>(",
                '    "pedidos", pedidoId, json);',
                "producer.send(evento);",
            ],
            "highlight": [{"token": "pedidoId"}],
            "steps": [
                {"atSec": 0.4, "lines": [1, 2], "note": "A chave é o pedidoId"},
                {"atSec": 1.6, "lines": [3, 3], "note": "Mesma chave, mesma partição"},
            ],
        },
        {
            "id": "cliente",
            "type": "animation",
            "durationSec": 3.6,
            "assetId": "celular-ordem-certa",
            "colors": "original",
        },
        {
            "id": "decisao",
            "type": "versus",
            "durationSec": 5.0,
            "title": "O que você decide",
            "left": {"title": "Ordem", "lines": ["vale por chave", "não no tópico inteiro"]},
            "right": {
                "title": "Paralelismo",
                "lines": ["até o número de partições", "consumidor a mais fica parado"],
            },
        },
        {
            "id": "fecho",
            "type": "end_card",
            "durationSec": 3.2,
            "variant": "next",
            "text": "Que chave você usaria?",
            "sub": "Parte 4: Kafka, RabbitMQ ou SQS?",
            "series": {"text": "Kafka", "part": 3, "total": 4},
        },
    ]
    narration = {
        "language": "pt-BR",
        "lines": [
            {
                "scene": "abertura",
                "text": "Pico do almoço, quatro consumidores na fila. "
                "E no celular do cliente, o pedido sai antes de ser pago.",
                "delivery": "hook",
            },
            {
                "scene": "fila",
                "text": "Numa fila com vários consumidores, uma reentrega pode trocar a ordem: "
                "o pago volta, e o saiu passa na frente.",
            },
            {
                "scene": "chave",
                "text": "No Kafka, o tópico tem partições, e a mesma chave cai sempre na mesma partição.",
                "delivery": "turn",
            },
            {
                "scene": "ordem",
                "text": "Quem lê a partição recebe na ordem em que foi escrito.",
                "delivery": "calm",
            },
            {
                "scene": "grupo",
                "text": "No grupo, cada partição tem um consumidor por vez. O quarto fica parado.",
            },
            {
                "scene": "codigo",
                "text": "Em Java, a chave é o pedidoId, o segundo argumento do ProducerRecord.",
            },
            {
                "scene": "cliente",
                "text": "E no celular do cliente, os avisos voltam a chegar na ordem certa.",
            },
            {
                "scene": "decisao",
                "text": "A ordem vale por chave. E as partições limitam os consumidores do grupo.",
            },
            {
                "scene": "fecho",
                "text": "E no seu sistema, qual seria a chave dos eventos? Conta aqui embaixo.",
                "delivery": "invite",
            },
        ],
    }
    return EPISODE_ID, content, narration, [celular_ordem_errada(), celular_ordem_certa()]
