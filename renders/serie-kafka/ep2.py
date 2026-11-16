"""Episódio 2 da série Kafka: fila × log, por que no Kafka a mensagem não some.

Cenário (cenarios.md): às 15h o time descobre um bug na regra do antifraude, ativo desde as 14h.
Fontes de cada fala: short-kafka-fila-log-pt/fontes.md. Horários e números das células são do cenário,
não medição. Gerado por gerar.py (`uv run --no-sync python renders/serie-kafka/gerar.py ep2`).
"""

import gerar
import lottie_celular as cel
import lottie_fluxo as fx

EPISODE_ID = "short-kafka-fila-log-pt"
FOOTER = "Fontes: docs do Apache Kafka 4.4, RabbitMQ e Amazon SQS · app fictício"
HORAS = ["13:40", "13:50", "14:00", "14:10", "14:20", "14:30", "14:40", "14:50"]
DESDE_14H = 2  # índice da célula das 14h
FITA = HORAS[:6]  # as seis primeiras células cabem grandes no vertical


def phone_15h(scene, header):
    """O mesmo aparelho de lottie_celular.phone, com a hora do cenário (15h)."""
    end = scene.seconds
    scene.text(header, cel.W / 2, 50, 46, cel.MUTED, 0, end, justify=2)
    body = cel.rect(cel.PHONE_W, cel.PHONE_H, 110, cel.BODY, cel.EDGE, 8)
    scene.shape("corpo", body, 0, end, cel.PHONE_X, cel.PHONE_Y)
    screen = cel.rect(cel.PHONE_W - 50, cel.PHONE_H - 50, 86, cel.SCREEN)
    scene.shape("tela", screen, 0, end, cel.PHONE_X, cel.PHONE_Y)
    scene.shape("camera", cel.rect(170, 42, 21, cel.BODY), 0, end, cel.PHONE_X, cel.PHONE_TOP + 58)
    scene.text("15:02", cel.PHONE_X, 215, 96, cel.WHITE, 0, end, justify=2)
    scene.text("sexta-feira", cel.PHONE_X, 300, 36, cel.MUTED, 0, end, justify=2)


# Cada cartão desce junto do trecho falado (voz clonada ~2,9 palavras/s, medida no ep1):
# "Três da tarde." (capa, já na tela) · "bug" é a 8ª palavra (~2,4 s) · "analisar" é a 19ª (~6,2 s).
BUG_AT, BUG_ALERT_AT, REANALISAR_AT = 2.1, 2.5, 5.9


def celular_alerta():
    s = cel.Scene(REANALISAR_AT + 1.0, REANALISAR_AT + 0.5, "celular-alerta")  # para no último quadro
    phone_15h(s, "App de delivery · Kafka")
    cel.notification(s, 0, "Pagamentos aprovados", "Antifraude: tudo certo", "check", cel.GREEN, 0)
    cel.notification(
        s,
        1,
        "Bug no antifraude",
        "Regra errada desde as 14h",
        "alerta",
        cel.CORAL,
        BUG_AT,
        alert_at=BUG_ALERT_AT,
    )
    cel.notification(s, 2, "Reanalisar desde as 14h", "Pedido do time", "spinner", cel.BLUE, REANALISAR_AT)
    return s


def celulas(affected=False):
    return [
        {
            "value": f"#{i + 1}",
            "label": hora,
            **({"state": "cost"} if affected and i >= DESDE_14H else {}),
        }
        for i, hora in enumerate(HORAS)
    ]


def anim_fila():
    """Fala (5,9 s): "Se ele lê de uma fila, não tem como. No RabbitMQ e no SQS, a mensagem sai quando
    o consumidor termina." A mensagem da frente vai ao antifraude e some;
    a legenda entra em "a mensagem sai"."""
    return fx.fila(
        "fila-apaga",
        6.6,
        5.6,
        "Numa fila, ler é apagar",
        "Fila",
        "RabbitMQ · SQS",
        ["Antifraude"],
        lambda i: f"#{i + 1}",
        "lida = apagada",
        3.4,
        t0=0.6,
        period=1.1,
    )


def anim_log():
    """Fala (10,5 s): "No Kafka, o tópico é um log, e ler não apaga. Cada consumidor guarda só um número:
    o offset da próxima mensagem." As células lidas ficam verdes e continuam na fita."""
    fraude = [(0, 0)] + [(1.0 + 1.0 * i, i) for i in range(1, len(FITA))]
    avisos = [(0, 0)] + [(2.5 + 1.8 * i, i) for i in range(1, 4)]
    lidas = [(1.0 + 1.0 * (r + 1), r, r, fx.GREEN) for r in range(len(FITA) - 1)]
    return fx.log(
        "log-fica",
        10.2,
        9.0,
        "No Kafka, ler não apaga",
        FITA,
        [
            {"label": "antifraude", "color": cel.GOLD, "side": "right", "steps": fraude},
            {"label": "avisos", "color": cel.BLUE, "side": "left", "steps": avisos},
        ],
        "lida, e continua lá",
        3.0,
        marks=lidas,
    )


def anim_volta():
    """Fala (4,0 s): "Corrigiu o bug? Volta o offset para as duas e reprocessa."
    Células desde as 14h em coral;
    o ponteiro volta às 14h e relê, deixando cada célula verde."""
    last = len(FITA) - 1
    fraude = [(0, last), (1.2, DESDE_14H)] + [
        (2.6 + 0.45 * k, r) for k, r in enumerate(range(DESDE_14H + 1, last + 1))
    ]
    relidas = [(2.6 + 0.45 * k, r, r, fx.GREEN) for k, r in enumerate(range(DESDE_14H, last))]
    relidas.append((2.6 + 0.45 * (last - DESDE_14H), last, last, fx.GREEN))
    return fx.log(
        "log-volta",
        6.0,
        5.4,
        "Volta o offset para as 14h",
        FITA,
        [{"label": "antifraude", "color": cel.GOLD, "side": "right", "steps": fraude}],
        "volta para as 14h e relê",
        1.3,
        marks=[(0.2, DESDE_14H, last, fx.CORAL), *relidas],
    )


def episode():
    content = gerar.base(["celular-alerta", "fila-apaga", "log-fica", "log-volta"])
    content["footer"] = FOOTER
    content["scenes"] = [
        {
            "id": "abertura",
            "type": "animation",
            "durationSec": 9.0,
            "assetId": "celular-alerta",
            "colors": "original",
        },
        {
            "id": "fila",
            "type": "animation",
            "durationSec": 7.0,
            "assetId": "fila-apaga",
            "colors": "original",
        },
        {"id": "log", "type": "animation", "durationSec": 10.6, "assetId": "log-fica", "colors": "original"},
        {
            "id": "volta",
            "type": "animation",
            "durationSec": 6.4,
            "assetId": "log-volta",
            "colors": "original",
        },
        {
            "id": "codigo",
            "type": "code",
            "durationSec": 4.4,
            "title": "Em Java, o consumidor",
            "lines": [
                "// regra corrigida",
                "consumer.seek(particao,",
                "    offsetDas14h);",
                "var lote = consumer.poll(tempo);",
            ],
            "highlight": [{"token": "seek"}],
            "steps": [
                {"atSec": 0.4, "lines": [2, 3], "note": "O ponteiro volta para as 14h"},
                {"atSec": 1.8, "lines": [4, 4], "note": "E lê de novo dali em diante"},
            ],
        },
        {
            "id": "decisao",
            "type": "versus",
            "durationSec": 7.4,
            "title": "O que muda no desenho",
            "left": {"title": "Fila", "lines": ["ler apaga a mensagem", "não dá para reler"]},
            "right": {
                "title": "Log no Kafka",
                "lines": ["apaga quando vence a retenção", "reler roda tudo de novo"],
            },
        },
        {
            "id": "fecho",
            "type": "end_card",
            "durationSec": 3.4,
            "variant": "next",
            "text": "Já precisou reprocessar?",
            "sub": "Parte 3: partição e chave",
            "series": {"text": "Kafka", "part": 2, "total": 4},
        },
    ]
    narration = {
        "language": "pt-BR",
        "lines": [
            {
                "scene": "abertura",
                "text": "Três da tarde. O time descobre um bug na regra do antifraude, ativo desde as duas, "
                "e precisa analisar de novo tudo o que passou.",
                "delivery": "hook",
            },
            {
                "scene": "fila",
                "text": "Se ele lê de uma fila, não tem como. No RabbitMQ e no SQS, "
                "a mensagem sai quando o consumidor termina.",
            },
            {
                "scene": "log",
                "text": "No Kafka, o tópico é um log, e ler não apaga. "
                "Cada consumidor guarda só um número: o offset da próxima mensagem.",
                "delivery": "turn",
            },
            {
                "scene": "volta",
                "text": "Corrigiu o bug? Volta o offset para as duas e reprocessa.",
                "delivery": "calm",
            },
            {
                "scene": "codigo",
                "text": "Em Java, um seek leva o consumidor de volta às duas, e ele lê de novo dali.",
            },
            {
                "scene": "decisao",
                "text": "O log só apaga quando vence a retenção que você configurou. "
                "E reprocessar roda tudo de novo, então o antifraude precisa ser idempotente.",
            },
            {
                "scene": "fecho",
                "text": "E você, já precisou reprocessar uma fila no trabalho?",
                "delivery": "invite",
            },
        ],
    }
    return EPISODE_ID, content, narration, [celular_alerta(), anim_fila(), anim_log(), anim_volta()]
