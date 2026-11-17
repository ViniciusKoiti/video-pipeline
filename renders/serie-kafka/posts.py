# ruff: noqa: E501 — textos dos posts, linhas longas de propósito
"""Série Kafka: rascunhos dos posts do YouTube (pt) no formato do Postiz, um por episódio.

Uso: uv run --no-sync python renders/serie-kafka/posts.py
Datas são PROPOSTA (o dono decide); a mídia entra depois do `vp postiz upload`. Nada é agendado aqui.
Integração: a mesma dos Shorts técnicos em pt (circuit breaker, idempotência).
"""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
INTEGRATION = "cmvx0omyy0005l26yggavdqpu"
FIM = "\n\nVoz clonada com IA. App, serviços e pedidos fictícios.\n\n#Shorts #Kafka #Java #SystemDesign #Backend"

POSTS = {
    "short-kafka-por-que-existe-pt": {
        "date": "2026-11-16T12:00:00-03:00",
        "title": "PEDIDO TRAVADO: POR QUE O KAFKA EXISTE",
        "content": (
            "Um app de delivery que chama cada serviço, um por vez, trava quando um deles cai. Com Kafka, o "
            "serviço de pedidos escreve o evento uma vez num tópico e segue; cada serviço lê no próprio ritmo, e "
            "quem caiu lê o que perdeu quando volta. O custo: um cluster a mais para operar, ou um serviço "
            "gerenciado.\n\nVocê ligaria seus serviços direto ou por um tópico? Responda nos comentários.\n\n"
            "Fonte: documentação do Apache Kafka 4.4 (Introduction e Design). Parte 1 de 4 da série Kafka."
        ),
    },
    "short-kafka-fila-log-pt": {
        "date": "2026-11-17T12:00:00-03:00",
        "title": "LER NÃO APAGA: FILA OU LOG NO KAFKA",
        "content": (
            "Às três da tarde, o time acha um bug no antifraude que vale desde as duas. Numa fila (RabbitMQ, SQS), "
            "a mensagem sai quando o consumidor termina. No Kafka, o tópico é um log: ler não apaga, e cada "
            "consumidor guarda só o offset da próxima mensagem. Corrigido o bug, um seek volta o offset e o "
            "consumidor relê dali. O log apaga pela retenção configurada, e reprocessar repete o efeito: o "
            "consumidor precisa ser idempotente.\n\nVocê já precisou reprocessar uma fila? Conta nos comentários."
            "\n\nFontes: documentação do Apache Kafka 4.4, do RabbitMQ (Streams) e do Amazon SQS. "
            "Parte 2 de 4 da série Kafka."
        ),
    },
    "short-kafka-particao-pt": {
        "date": "2026-11-18T12:00:00-03:00",
        "title": "PEDIDO EMBARALHADO? A CHAVE DO KAFKA RESOLVE",
        "content": (
            "No pico do almoço, quatro consumidores numa fila: uma reentrega pode trocar a ordem, e o \"saiu para "
            "entrega\" chega antes do \"pago\". No Kafka, o tópico tem partições; eventos com a mesma chave (o id "
            "do pedido) caem sempre na mesma partição e são lidos na ordem em que foram escritos. Num grupo, cada "
            "partição tem um consumidor por vez: com três partições, o quarto consumidor fica parado.\n\n"
            "Qual seria a chave dos eventos no seu sistema? Conta nos comentários.\n\n"
            "Fontes: documentação do Apache Kafka 4.4 e do RabbitMQ (Queues). Parte 3 de 4 da série Kafka."
        ),
    },
    "short-kafka-qual-usar-pt": {
        "date": "2026-11-19T12:00:00-03:00",
        "title": "KAFKA, RABBITMQ OU SQS: QUAL USAR?",
        "content": (
            "Redimensionar a foto do prato é tarefa: um worker faz uma vez e acabou, caso de fila. A fila do "
            "RabbitMQ é feita para esvaziar; o Amazon SQS fica na AWS, escala sem provisionar e guarda mensagens "
            "por até 14 dias. O \"pedido pago\" é histórico: vários serviços leem no próprio ritmo e podem reler, "
            "caso de log, o Kafka. E a fronteira borrou: o RabbitMQ tem streams, e o Kafka tem share groups.\n\n"
            "Qual desses três você usa no trabalho? Conta nos comentários.\n\n"
            "Fontes: documentação do Apache Kafka 4.4, do RabbitMQ (Queues e Streams) e do Amazon SQS. "
            "Parte 4 de 4 da série Kafka."
        ),
    },
}

INTEGRATION_EN = "cmvx0nn9g0003l26yf4npmb66"  # canal em inglês dos Shorts técnicos (circuit breaker en)
FIM_EN = (
    "\n\nThe author's voice is cloned with AI. Animations made for this video; fictional app, services and orders."
    "\n\n#Shorts #Kafka #Java #SystemDesign #Backend"
)

POSTS_EN = {
    "short-kafka-por-que-existe-en": {
        "date": "2026-11-16T12:00:00-03:00",
        "title": "ORDER STUCK: WHY KAFKA EXISTS",
        "content": (
            "A delivery app that calls each service one at a time stops when one of them goes down. With Kafka, the orders service writes the event once to a topic and moves on; each service reads at its own pace, and whoever was down reads what it missed when it comes back. The cost: one more cluster to run, or a managed service.\n\n"
            "Would you connect your services directly or through a topic? Tell me in the comments.\n\n"
            "Source: Apache Kafka 4.4 documentation (Introduction and Design). Part 1 of 4 of the Kafka series."
        ),
    },
    "short-kafka-fila-log-en": {
        "date": "2026-11-17T12:00:00-03:00",
        "title": "READING DOESN'T DELETE: QUEUE OR LOG IN KAFKA",
        "content": (
            "At 3 p.m., the team finds a bug in the fraud check that has been live since 2. In a queue (RabbitMQ, SQS), the message is removed when the consumer finishes. In Kafka, the topic is a log: reading doesn't delete, and each consumer keeps only the offset of the next message. Once the bug is fixed, a seek moves the offset back and the consumer re-reads from there. The log deletes by the configured retention, and reprocessing repeats the effect: the consumer has to be idempotent.\n\n"
            "Have you ever had to reprocess a queue? Tell me in the comments.\n\n"
            "Sources: Apache Kafka 4.4, RabbitMQ (Streams) and Amazon SQS documentation. Part 2 of 4 of the Kafka series."
        ),
    },
    "short-kafka-particao-en": {
        "date": "2026-11-18T12:00:00-03:00",
        "title": "SCRAMBLED ORDERS? KAFKA'S KEY FIXES IT",
        "content": (
            "Lunch rush, four consumers on a queue: a redelivery can change the order, and \"out for delivery\" arrives before \"paid\". In Kafka, the topic has partitions; events with the same key (the order id) always land in the same partition and are read in the order they were written. In a group, each partition has one consumer at a time: with three partitions, the fourth consumer sits idle.\n\n"
            "What would the event key be in your system? Tell me in the comments.\n\n"
            "Sources: Apache Kafka 4.4 and RabbitMQ (Queues) documentation. Part 3 of 4 of the Kafka series."
        ),
    },
    "short-kafka-qual-usar-en": {
        "date": "2026-11-19T12:00:00-03:00",
        "title": "KAFKA, RABBITMQ OR SQS: WHICH ONE?",
        "content": (
            "Resizing the dish photo is a task: a worker does it once and it's done, a queue. RabbitMQ's queue is built to empty out; Amazon SQS runs on AWS, scales without provisioning and keeps messages for up to 14 days. The \"order paid\" event is history: several services read at their own pace and can re-read, a log, Kafka. And the line has blurred: RabbitMQ has streams, and Kafka has share groups.\n\n"
            "Which of the three do you use at work? Tell me in the comments.\n\n"
            "Sources: Apache Kafka 4.4, RabbitMQ (Queues and Streams) and Amazon SQS documentation. Part 4 of 4 of the Kafka series."
        ),
    },
}


def post(item, integration=INTEGRATION, fim=FIM):
    return {
        "type": "schedule",
        "date": item["date"],
        "shortLink": False,
        "tags": [],
        "posts": [
            {
                "integration": {"id": integration},
                "value": [{"content": item["content"] + fim, "image": []}],
                "settings": {
                    "__type": "youtube",
                    "title": item["title"],
                    "type": "public",
                    "selfDeclaredMadeForKids": "no",
                },
            }
        ],
    }


def main():
    jobs = [(POSTS, "pt", INTEGRATION, FIM), (POSTS_EN, "en", INTEGRATION_EN, FIM_EN)]
    for posts, lang, integration, fim in jobs:
        for episode_id, item in posts.items():
            folder = BASE / episode_id / "posts"
            folder.mkdir(parents=True, exist_ok=True)
            data = json.dumps(post(item, integration, fim), ensure_ascii=False, indent=1) + "\n"
            (folder / f"post-youtube-{lang}.json").write_text(data, encoding="utf-8")
            print(episode_id, len(item["title"]), "chars no título")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
