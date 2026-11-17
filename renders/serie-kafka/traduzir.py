# ruff: noqa: E501 — dicionários de texto, linhas longas de propósito
"""Série Kafka em inglês: gera cada episódio -en a partir do pt já montado (mesmas cenas, tempos e animações).

Uso: uv run --no-sync python renders/serie-kafka/traduzir.py [ep1 ...]
Troca só os textos (tela, código, notificações do celular) pelo dicionário do episódio e escreve a narração em
inglês. Texto em pt sem tradução é erro. Pasta de produção: data/episodes/<base>-en/ com traducao.json (ADR 034);
cópia versionável: renders/serie-kafka/<base>-en/. Fontes: as mesmas do pt (fontes.md, textos já em inglês).
"""

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar  # noqa: E402

ROOT, BASE = gerar.ROOT, gerar.BASE
SKIP = {"id", "type", "assetId", "colors", "path", "kind", "state", "node", "from", "to", "style", "locale",
        "format", "safeArea", "variant", "side", "direction", "layout", "mode", "winner", "f", "fName",
        "fFamily", "fStyle", "cm", "v", "ty", "mn", "nm"}  # nm: nome de camada, não aparece
KEEP = re.compile(r"^(\d+|#\d+|offset \d+|12:04|Kafka|RabbitMQ|Amazon SQS|Streams|Share groups|log|send|seek|"
                  r"producer\.send\(event\);|RabbitMQ, SQS|RabbitMQ · SQS|Kafka · RabbitMQ · SQS|worker \d|Workers|"
                  r"(el|fl|sh|st|tm|rc))$")

COMUM = {
    "App de delivery · Kafka": "Delivery app · Kafka",
    "sexta-feira, almoço": "Friday, lunchtime",
    "sexta-feira": "Friday",
    "Pagamento aprovado": "Payment approved",
    "Seu pedido foi pago": "Your order is paid",
    "Pedidos": "Orders",
    "Pagamento": "Payments",
    "Restaurante": "Restaurant",
    "Entregador": "Courier",
    "Notificação": "Notifications",
    "O que muda no desenho": "What changes in the design",
    "Fila": "Queue",
    "Antifraude": "Fraud check",
}

TELA = {
    "ep1": {
        "Fonte: documentação do Apache Kafka 4.4 · app e serviços fictícios": "Source: Apache Kafka 4.4 docs · fictional app and services",
        "Chamada direta, um por um": "Direct calls, one by one",
        "Com Kafka: escreve uma vez": "With Kafka: write once",
        "Tópico pedidos": "orders topic",
        "escreve": "writes",
        "pedido #123": "order #123",
        "pedido #124": "order #124",
        "Em Java, o produtor": "In Java, the producer",
        "var evento = new ProducerRecord<>(": "var event = new ProducerRecord<>(",
        '    "pedidos", id, json);': '    "orders", id, json);',
        "producer.send(evento);": "producer.send(event);",
        '"pedidos"': '"orders"',
        "O evento vai para o tópico pedidos": "The event goes to the orders topic",
        "Não espera nenhum consumidor": "It waits for no consumer",
        "O Entregador caiu: o evento espera": "Courier down: the event waits",
        "volta e lê": "back, reads",
        "Chamada direta": "Direct call",
        "simples de começar": "simple to start",
        "um serviço caído trava o resto": "one service down blocks the rest",
        "Tópico no Kafka": "Kafka topic",
        "serviços desacoplados": "decoupled services",
        "um cluster a mais para operar": "one more cluster to run",
        "Direto ou por um tópico?": "Direct or through a topic?",
        "Parte 2: por que a mensagem não some": "Part 2: why the message doesn't vanish",
        "o pedido parou": "the order stopped",
        "Aguarde um instante": "Just a moment",
        "Procurando entregador": "Finding a courier",
        "Preparando seu pedido": "Preparing your order",
        "Restaurante aceitou": "Restaurant accepted",
        "Chega em instantes": "Arriving shortly",
        "Entregador a caminho": "Courier on the way",
        "Aguardando o entregador": "Waiting for the courier",
        "Pedido pronto": "Order ready",
        "Do lado do cliente": "On the customer's side",
    },
    "ep2": {
        "Fontes: docs do Apache Kafka 4.4, RabbitMQ e Amazon SQS · app fictício": "Sources: Apache Kafka 4.4, RabbitMQ and Amazon SQS docs · fictional app",
        "Em Java, o consumidor": "In Java, the consumer",
        "// regra corrigida": "// rule fixed",
        "consumer.seek(particao,": "consumer.seek(partition,",
        "    offsetDas14h);": "    offsetAt2pm);",
        "var lote = consumer.poll(tempo);": "var batch = consumer.poll(timeout);",
        "O ponteiro volta para as 14h": "The offset goes back to 2 PM",
        "E lê de novo dali em diante": "And it reads again from there",
        "ler apaga a mensagem": "reading deletes the message",
        "não dá para reler": "no way to re-read",
        "Log no Kafka": "Log in Kafka",
        "apaga quando vence a retenção": "deleted when retention runs out",
        "reler roda tudo de novo": "re-reading runs it all again",
        "Já precisou reprocessar?": "Ever had to reprocess?",
        "Parte 3: partição e chave": "Part 3: partition and key",
        "Pedido do time": "Request from the team",
        "Reanalisar desde as 14h": "Re-check since 2 PM",
        "Regra errada desde as 14h": "Wrong rule since 2 PM",
        "Bug no antifraude": "Bug in the fraud check",
        "Antifraude: tudo certo": "Fraud check: all clear",
        "Pagamentos aprovados": "Payments approved",
        "15:02": "3:02",
        "lida = apagada": "read = deleted",
        "Numa fila, ler é apagar": "In a queue, reading deletes",
        "lida, e continua lá": "read, and still there",
        "avisos": "alerts",
        "antifraude": "fraud check",
        "13:40": "1:40 PM", "13:50": "1:50 PM", "14:00": "2:00 PM", "14:10": "2:10 PM",
        "14:20": "2:20 PM", "14:30": "2:30 PM", "14:40": "2:40 PM", "14:50": "2:50 PM",
        "No Kafka, ler não apaga": "In Kafka, reading doesn't delete",
        "volta para as 14h e relê": "back to 2 PM, read again",
        "Volta o offset para as 14h": "Rewind the offset to 2 PM",
    },
    "ep3": {
        "Fonte: docs do Apache Kafka 4.4 e do RabbitMQ · app e serviços fictícios": "Sources: Apache Kafka 4.4 and RabbitMQ docs · fictional app and services",
        "Fila: a reentrega troca a ordem": "Queue: redelivery changes the order",
        "fila comum": "plain queue",
        "Consumidor 1": "Consumer 1", "Consumidor 2": "Consumer 2",
        "Consumidor 3": "Consumer 3", "Consumidor 4": "Consumer 4",
        "#7 pago": "#7 paid", "#7 saiu": "#7 shipped", "#3 criado": "#3 created",
        "#7 criado": "#7 created", "#9 criado": "#9 created", "#3 pago": "#3 paid",
        "volta": "back",
        "Mesma chave, mesma partição": "Same key, same partition",
        "Produtor": "Producer",
        "chave pedidoId": "key orderId",
        "Partição 0": "Partition 0", "Partição 1": "Partition 1", "Partição 2": "Partition 2",
        "Na partição, a ordem é a de escrita": "In a partition, write order holds",
        "Part. 0": "Part. 0", "Part. 1": "Part. 1", "Part. 2": "Part. 2",
        "Um consumidor por partição": "One consumer per partition",
        "sem partição": "no partition",
        "Em Java, a chave do evento": "In Java, the event key",
        "var evento = new ProducerRecord<>(": "var event = new ProducerRecord<>(",
        '    "pedidos", pedidoId, json);': '    "orders", orderId, json);',
        "producer.send(evento);": "producer.send(event);",
        "pedidoId": "orderId",
        "A chave é o pedidoId": "The key is orderId",
        "O que você decide": "What you decide",
        "Ordem": "Order",
        "vale por chave": "holds per key",
        "não no tópico inteiro": "not across the topic",
        "Paralelismo": "Parallelism",
        "até o número de partições": "up to the partition count",
        "consumidor a mais fica parado": "extra consumers sit idle",
        "Que chave você usaria?": "Which key would you use?",
        "Parte 4: Kafka, RabbitMQ ou SQS?": "Part 4: Kafka, RabbitMQ or SQS?",
        "fora de ordem": "out of order",
        "O entregador já pegou": "The courier picked it up",
        "Saiu para entrega": "Out for delivery",
        "Seu pedido foi registrado": "Your order was placed",
        "Pedido #7 criado": "Order #7 created",
        "Com a chave pedidoId": "With orderId as the key",
    },
    "ep4": {
        "Fontes: docs Apache Kafka 4.4, RabbitMQ e Amazon SQS · app fictício": "Sources: Apache Kafka 4.4, RabbitMQ and Amazon SQS docs · fictional app",
        "Duas filas": "Two queues",
        "fila FIFO": "FIFO queue",
        "feita para esvaziar": "built to empty out",
        "hospedada na AWS": "hosted on AWS",
        "escala sem provisionar": "scales without provisioning",
        "guarda até 14 dias": "keeps up to 14 days",
        "A fronteira borrou": "The line has blurred",
        "filas": "queues",
        "log que se relê": "a log you re-read",
        "dividem a partição": "share a partition",
        "também": "also",
        "relê": "re-read",
        "divide": "share",
        "Melhor para quê?": "Best for what?",
        "tarefa que some depois de feita": "a task that's gone once done",
        "Log": "Log",
        "histórico que vários releem": "history many services re-read",
        "Qual você usa no trabalho?": "Which one do you use at work?",
        "Fim da série Kafka": "End of the Kafka series",
        "Pedido #123 pago": "Order #123 paid",
        "Painel do restaurante": "Restaurant dashboard",
        "Foto do prato enviada": "Dish photo uploaded",
        "feita = sai da fila": "done = off the queue",
        "fotos do prato": "dish photos",
        "Tarefa: faz uma vez e acabou": "A task: done once, gone",
        "e pode voltar e reler": "and can go back and re-read",
        "Dados": "Data",
        "Notificação": "Alerts",
        "#125 pago": "#125 paid", "#124 pago": "#124 paid", "#123 pago": "#123 paid",
        "#122 pago": "#122 paid", "#121 pago": "#121 paid", "#120 pago": "#120 paid",
        "Cada um lê no seu ritmo": "Each reads at its own pace",
    },
}

FALA = {
    "ep1": [
        "Noon on a delivery app. Every step of the order becomes a notification on your phone. Until one service goes down, and everything stops.",
        "The orders service calls one service at a time and waits. If the courier service goes down, it's stuck.",
        "With Kafka, it writes the event once to a topic and moves on. Each service reads at its own pace.",
        "In Java, it's a send to the orders topic, and the service moves on without waiting for anyone.",
        "If the courier service goes down, the event stays stored in the topic, and it reads it when it comes back.",
        "And on the customer's phone, the notifications keep coming in.",
        "The gain is decoupling. The cost is a cluster to run, or a managed service.",
        "Would you connect your services directly, or through a topic?",
    ],
    "ep2": [
        "Three in the afternoon. The team finds a bug in the fraud check rule, live since two, and has to re-check everything that went through.",
        "If it reads from a queue, there's no way. In RabbitMQ and SQS, the message is removed when the consumer finishes.",
        "In Kafka, the topic is a log, and reading doesn't delete. Each consumer keeps just a single number: the offset of the next message.",
        "Bug fixed? Move the offset back to two and reprocess.",
        "In Java, a seek takes the consumer back to two, and it reads again from there.",
        "The log only deletes when the retention you configured runs out. And reprocessing runs everything again, so the fraud check has to be idempotent.",
        "And you, have you ever had to reprocess a queue at work?",
    ],
    "ep3": [
        "Lunch rush, four consumers on the queue. And on the customer's phone, the order ships before it's paid.",
        "In a queue with several consumers, a redelivery can change the order: paid comes back, and shipped jumps ahead.",
        "In Kafka, the topic has partitions, and the same key always lands in the same partition.",
        "Whoever reads the partition gets the events in the order they were written.",
        "In a group, each partition has one consumer at a time. The fourth one sits idle.",
        "In Java, the key is orderId, the second argument of ProducerRecord.",
        "And on the customer's phone, the notifications arrive in the right order again.",
        "Order holds per key. And partitions cap the consumers in a group.",
        "In your system, what would the event key be? Tell me below.",
    ],
    "ep4": [
        "In the app, the dish photo needs resizing, and the paid order notifies four services. The candidates: Kafka, RabbitMQ and SQS.",
        "The photo is a task: a worker does it once, and it's done. That's a queue.",
        "RabbitMQ's queue is built to empty out. SQS lives on AWS, scales on its own and keeps messages for up to fourteen days.",
        "The paid order is history: four services read at their own pace and can read again. That's a log, Kafka.",
        "But the line has blurred: RabbitMQ has streams, which can be re-read, and Kafka has share groups.",
        "So it depends: a task that disappears, queue. History that many re-read, log.",
        "And you, which of these three do you use at work today?",
    ],
}


# Celular da abertura no ritmo da fala em inglês: (segundo no pt, segundo no en), estimado pela posição do trecho
# no WAV em inglês. Só a linha do tempo da animação muda; o desenho e o content.json (números) ficam iguais ao pt.
WARP = {
    "ep1": {"celular-abertura": [(0, 0), (2.0, 2.0), (3.4, 3.6), (6.0, 6.3), (6.6, 8.1), (6.9, 8.4), (7.4, 8.9)]},
    "ep2": {"celular-alerta": [(0, 0), (2.1, 2.8), (2.5, 3.2), (5.9, 7.2), (6.4, 7.7), (6.9, 8.2)]},
    "ep3": {"celular-ordem-errada": [(0, 0), (4.5, 5.6), (5.5, 6.6), (6.1, 7.0), (6.3, 7.1), (6.7, 7.2), (7.2, 7.5)]},
    "ep4": {"celular-dois-trabalhos": [(0, 0), (3.7, 3.9), (5.5, 6.4), (6.0, 6.9), (6.4, 7.3)]},
}


def retime(data, anchors):
    """Reescala os tempos (quadros) da animação por uma função linear por partes e crescente."""
    fps = data["fr"]

    def f(frame_value):
        sec = frame_value / fps
        for (a0, b0), (a1, b1) in zip(anchors, anchors[1:], strict=False):
            if sec <= a1:
                return round((b0 + (b1 - b0) * (sec - a0) / (a1 - a0)) * fps, 3)
        a, b = anchors[-1]
        return round((b + sec - a) * fps, 3)

    def walk(node):
        if isinstance(node, dict):
            for key in ("ip", "op", "tm"):
                if isinstance(node.get(key), (int, float)):
                    node[key] = round(f(node[key]))
            if isinstance(node.get("t"), (int, float)) and any(k in node for k in ("s", "h", "e", "i")):
                node["t"] = f(node["t"])
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)
    return data


def translate(obj, table, missing, key=None):
    if isinstance(obj, dict):
        return {k: (v if k in SKIP else translate(v, table, missing, k)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [translate(v, table, missing, key) for v in obj]
    if isinstance(obj, str):
        if obj in table:
            return table[obj]
        if not KEEP.match(obj):
            missing.add(obj)
    return obj


def build(name):
    episode_id, content, narration, animations = gerar.episodes()[name]()
    base_id = episode_id.removesuffix("-pt")
    table = {**COMUM, **TELA[name]}
    missing = set()
    content_en = translate({k: v for k, v in content.items() if k != "assets"}, table, missing)
    content_en["assets"] = content["assets"]
    content_en["locale"] = "en"
    lotties = {a.name: translate(json.loads(a.finish()), table, missing) for a in animations}
    for asset, anchors in WARP.get(name, {}).items():
        lotties[asset] = retime(lotties[asset], anchors)
    assert not missing, f"{name}: texto sem tradução: {sorted(missing)}"
    lines = narration["lines"]
    assert len(FALA[name]) == len(lines), f"{name}: {len(FALA[name])} falas em inglês, {len(lines)} no pt"
    narration_en = {"language": "en", "lines": [{**line, "text": text} for line, text in zip(lines, FALA[name], strict=True)]}
    return episode_id, f"{base_id}-en", content_en, narration_en, lotties


def write(source_id, episode_id, content, narration, lotties):
    production, versioned = ROOT / "data/episodes" / episode_id, BASE / episode_id
    (production / "public/lottie").mkdir(parents=True, exist_ok=True)
    (versioned / "lottie").mkdir(parents=True, exist_ok=True)
    licencas = {}
    for name, data in lotties.items():
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
        for folder in (production / "public/lottie", versioned / "lottie"):
            (folder / f"{name}.json").write_text(text, encoding="utf-8")
        licencas[name] = {"license": "Original", "author": "projeto (renders/serie-kafka/traduzir.py)",
                          "sha256": hashlib.sha256(text.encode()).hexdigest(),
                          "usage_notes": "Formas geométricas e texto; sem pessoas, marcas ou imagem externa."}
    dump = lambda obj: json.dumps(obj, ensure_ascii=False, indent=2) + "\n"  # noqa: E731
    (production / "content.json").write_text(dump(content), encoding="utf-8")
    (production / "narracao.json").write_text(dump(narration), encoding="utf-8")
    link = {"derived_from": source_id, "language": "en", "source_language": "pt-BR"}
    (production / "traducao.json").write_text(json.dumps(link, ensure_ascii=False) + "\n", encoding="utf-8")
    (versioned / "content.en.json").write_text(dump(content), encoding="utf-8")
    (versioned / "narracao.en.json").write_text(dump(narration), encoding="utf-8")
    (versioned / "licencas.json").write_text(dump(licencas), encoding="utf-8")
    words = sum(len(line["text"].split()) for line in narration["lines"])
    print(f"{episode_id}: {len(content['scenes'])} cenas, {words} palavras")


def main(argv):
    for name in argv or list(FALA):
        write(*build(name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
