"""Série Kafka, episódio 4: Kafka, RabbitMQ ou SQS — qual usar? (pt)

Cenário: dois trabalhos no mesmo app de delivery: redimensionar a foto do prato que o restaurante
envia (tarefa) e avisar quatro serviços que o pedido foi pago (histórico). "Melhor" vira "melhor para
quê": cada opção pelo que a própria documentação diz.
Fontes por fala em short-kafka-qual-usar-pt/fontes.md. Nada aqui é medição.
"""

import gerar
import lottie_celular as cel
import lottie_fluxo as fx

EPISODE_ID = "short-kafka-qual-usar-pt"
FOOTER = "Fontes: docs Apache Kafka 4.4, RabbitMQ e Amazon SQS · app fictício"
LEITORES = ["Loja", "Aviso", "Rota", "Dados"]  # serviços que leem o pedido pago (rótulo ≤ 6)


# Tempos (s) casados com a fala da abertura a ~2,9 palavras/s (ritmo da voz clonada no ep1):
# "foto do prato" ~1,0 s (o cartão já está no quadro 0, que é a capa); "pedido pago" ~3,9 s;
# "Os candidatos" ~5,7 s. O Lottie para no último quadro; a cena pode durar mais.
FALA_PEDIDO_PAGO, FALA_CANDIDATOS = 3.7, 5.5


def celular_dois_trabalhos():
    s = cel.Scene(6.4, 6.0, "celular-dois-trabalhos")
    cel.phone(s, "App de delivery · Kafka")
    cel.notification(s, 0, "Foto do prato enviada", "Painel do restaurante", "check", cel.GOLD, 0)
    cel.notification(s, 1, "Pagamento aprovado", "Pedido #123 pago", "check", cel.GREEN, FALA_PEDIDO_PAGO)
    s.text(
        "Kafka · RabbitMQ · SQS",
        cel.W / 2,
        cel.SLOT_TOP + 2 * cel.SLOT_GAP,
        46,
        cel.GOLD,
        FALA_CANDIDATOS,
        s.seconds,
        justify=2,
    )
    return s


def ponteiros():
    """Quatro leitores do mesmo log, cada um no seu ritmo; o Dados volta ao começo e relê."""
    passos = {
        "Loja": [(0.8, 1), (1.6, 3), (2.2, 5), (2.8, 7)],
        "Aviso": [(0.8, 2), (2.2, 4), (2.8, 6)],
        "Rota": [(0.8, 0), (1.6, 1), (2.8, 3)],
        "Dados": [(0.8, 3), (1.6, 4), (2.2, 6), (2.8, 0), (3.4, 1)],
    }
    return [
        {"label": nome, "steps": [{"atSec": t, "index": i} for t, i in passos[nome]]} for nome in LEITORES
    ]


def anim_tarefa():
    """Fala (5,0 s): "A foto é tarefa: um worker faz uma vez, e acabou. Isso é fila."
    Cada foto vai a um worker
    e sai da fila; a legenda entra em "e acabou"."""
    return fx.fila(
        "fila-tarefa",
        5.6,
        5.0,
        "Tarefa: faz uma vez e acabou",
        "Fila",
        "fotos do prato",
        ["1", "2", "3"],
        lambda i: f"#{i + 1}",
        "feita = sai da fila",
        2.4,
        t0=0.5,
        period=0.75,
        header="Workers",
    )


def anim_historico():
    """Fala (6,6 s): "O pedido pago é histórico: quatro serviços leem no seu ritmo e podem reler.
    É log, o Kafka."
    Quatro ponteiros em ritmos diferentes; o Dados volta ao começo em "podem reler"."""
    pedidos = [f"#{120 + i} pago" for i in range(6)]
    leitores = [
        {
            "label": "Restaurante",
            "color": cel.GOLD,
            "side": "right",
            "steps": [(0, 1), (1.2, 3), (2.4, 5)],
        },
        {
            "label": "Entregador",
            "color": cel.BLUE,
            "side": "right",
            "steps": [(0, 0), (1.6, 2), (3.2, 4)],
        },
        {
            "label": "Notificação",
            "color": cel.VIOLET,
            "side": "left",
            "steps": [(0, 0), (1.8, 1), (3.4, 2), (5.0, 3)],
        },
        {
            "label": "Dados",
            "color": cel.GREEN,
            "side": "left",
            "steps": [(0, 2), (1.2, 4), (2.4, 5), (3.8, 0), (4.6, 1), (5.4, 2)],
        },
    ]
    return fx.log(
        "log-historico",
        6.4,
        5.8,
        "Cada um lê no seu ritmo",
        pedidos,
        leitores,
        "e pode voltar e reler",
        3.8,
    )


def episode():
    content = gerar.base(["celular-dois-trabalhos", "fila-tarefa", "log-historico"])
    content["footer"] = FOOTER
    content["scenes"] = [
        {
            "id": "abertura",
            "type": "animation",
            "durationSec": 7.8,
            "assetId": "celular-dois-trabalhos",
            "colors": "original",
        },
        {
            "id": "tarefa",
            "type": "animation",
            "durationSec": 6.0,
            "assetId": "fila-tarefa",
            "colors": "original",
        },
        {
            "id": "filas",
            "type": "versus",
            "durationSec": 6.2,
            "title": "Duas filas",
            "left": {"title": "RabbitMQ", "lines": ["fila FIFO", "feita para esvaziar"]},
            "right": {
                "title": "Amazon SQS",
                "lines": ["hospedada na AWS", "escala sem provisionar", "guarda até 14 dias"],
            },
        },
        {
            "id": "historico",
            "type": "animation",
            "durationSec": 6.9,
            "assetId": "log-historico",
            "colors": "original",
        },
        {
            "id": "fronteira",
            "type": "flow",
            "durationSec": 6.6,
            "title": "A fronteira borrou",
            "legend": False,
            "direction": "right",
            "nodes": [
                {"id": "rabbit", "label": "RabbitMQ", "sublabel": "filas", "column": 0, "lane": 0},
                {"id": "streams", "label": "Streams", "sublabel": "log que se relê", "column": 1, "lane": 0},
                {"id": "kafka", "label": "Kafka", "sublabel": "log", "column": 0, "lane": 1},
                {
                    "id": "share",
                    "label": "Share groups",
                    "sublabel": "dividem a partição",
                    "column": 1,
                    "lane": 1,
                },
            ],
            "edges": [
                {"from": "rabbit", "to": "streams", "label": "também"},
                {"from": "kafka", "to": "share", "label": "também"},
            ],
            "states": [
                {"node": "rabbit", "atSec": 1.3, "state": "running"},
                {"node": "streams", "atSec": 2.2, "state": "running"},
                {"node": "kafka", "atSec": 2.8, "state": "running"},
                {"node": "share", "atSec": 3.7, "state": "running"},
            ],
            "tokens": [
                {
                    "id": "rele",
                    "from": "rabbit",
                    "to": "streams",
                    "atSec": 1.4,
                    "durationSec": 0.8,
                    "label": "relê",
                },
                {
                    "id": "divide",
                    "from": "kafka",
                    "to": "share",
                    "atSec": 2.9,
                    "durationSec": 0.8,
                    "label": "divide",
                },
            ],
        },
        {
            "id": "decisao",
            "type": "versus",
            "durationSec": 5.2,
            "title": "Melhor para quê?",
            "left": {"title": "Fila", "lines": ["tarefa que some depois de feita", "RabbitMQ, SQS"]},
            "right": {"title": "Log", "lines": ["histórico que vários releem", "Kafka"]},
        },
        {
            "id": "fecho",
            "type": "end_card",
            "durationSec": 3.2,
            "variant": "follow",
            "text": "Qual você usa no trabalho?",
            "sub": "Fim da série Kafka",
            "series": {"text": "Kafka", "part": 4, "total": 4},
        },
    ]
    narration = {
        "language": "pt-BR",
        "lines": [
            {
                "scene": "abertura",
                "text": "No app, a foto do prato precisa ser redimensionada, e o pedido pago avisa "
                "quatro serviços. Os candidatos: Kafka, RabbitMQ e SQS.",
                "delivery": "hook",
            },
            {
                "scene": "tarefa",
                "text": "A foto é tarefa: um worker faz uma vez, e acabou. Isso é fila.",
                "delivery": "calm",
            },
            {
                "scene": "filas",
                "text": "A fila do RabbitMQ é feita para esvaziar. "
                "O SQS fica na AWS, escala sozinho e guarda até catorze dias.",
            },
            {
                "scene": "historico",
                "text": "O pedido pago é histórico: quatro serviços leem no seu ritmo e podem reler. "
                "É log, o Kafka.",
                "delivery": "turn",
            },
            {
                "scene": "fronteira",
                "text": "Mas a fronteira borrou: o RabbitMQ tem streams, que se releem, "
                "e o Kafka tem share groups.",
            },
            {
                "scene": "decisao",
                "text": "Então depende: tarefa que some, fila. Histórico que vários releem, log.",
                "delivery": "calm",
            },
            {
                "scene": "fecho",
                "text": "E você, qual desses três usa hoje no trabalho?",
                "delivery": "invite",
            },
        ],
    }
    return EPISODE_ID, content, narration, [celular_dois_trabalhos(), anim_tarefa(), anim_historico()]
