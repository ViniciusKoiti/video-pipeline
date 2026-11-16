# Fontes do episódio 2 — Fila × log (short-kafka-fila-log-pt)

Textos baixados em 2026-11-15, numerados por parágrafo em `renders/serie-kafka/fontes/` (ids em `../serie.md`).
Cenário fictício: antifraude de um app de delivery, bug na regra desde as 14h, descoberto às 15h. Horários das
células (`13:40`…`14:50`), `#1`…`#8` e o nome dos ponteiros (`fraude`, `avisos`) são do cenário. Sem medição.

| Cena | Fala ou tela | Fonte | Trecho literal |
| --- | --- | --- | --- |
| `abertura` | "Três da tarde. O time descobre um bug na regra do antifraude, ativo desde as duas, e precisa analisar de novo tudo o que passou."; celular com "Bug no antifraude" e "Reanalisar desde as 14h" | cenário | — |
| `fila` | "No RabbitMQ (…) a mensagem sai quando o consumidor termina"; tela "Numa fila, ler é apagar" | R-S P23 | "As all current RabbitMQ queue types have destructive consume behaviour, i.e. messages are deleted from the queue when a consumer is finished with them, it is not possible to re-read messages that have been consumed." |
| `fila` | "(…) e no SQS, a mensagem sai quando o consumidor termina" | SQS-W P22–P23 | "While message A is being processed, it remains in the queue and isn't returned to subsequent receive requests for the duration of the visibility timeout." / "The consumer (Component 2) deletes message A from the queue to prevent the message from being received and processed again when the visibility timeout expires." |
| `fila` | "Se ele lê de uma fila, não tem como [analisar de novo]" | R-S P23 (fila do RabbitMQ); SQS-W P23 (apagada para não ser recebida de novo) | ver acima: "it is not possible to re-read messages that have been consumed" |
| `log` | "No Kafka, o tópico é um log" | K-DES P11; K-DES P58 | "a design with a number of unique elements, more akin to a database log than a traditional messaging system" / "The consumer specifies its offset in the log with each request and receives back a chunk of log beginning from that position." |
| `log` | "ler não apaga"; tela "No Kafka, ler não apaga" | K-INT P32 | "Events in a topic can be read as often as needed-unlike traditional messaging systems, events are not deleted after consumption." |
| `log` | "Cada consumidor guarda só um número: o offset da próxima mensagem" | K-DES P68 | "This means that the position of a consumer in each partition is just a single integer, the offset of the next message to consume." |
| `volta`, `codigo` | "Corrigiu o bug? Volta o offset para as duas e reprocessa."; tela "Volta o offset para as 14h"; nota "O ponteiro volta para as 14h" | K-DES P69 | "A consumer can deliberately rewind back to an old offset and re-consume data. (…) For example, if the consumer code has a bug and is discovered after some messages are consumed, the consumer can re-consume those messages once the bug is fixed." |
| `codigo` | "Em Java, um seek leva o consumidor de volta às duas, e ele lê de novo dali."; `consumer.seek(particao, offsetDas14h)` e `consumer.poll(tempo)` | código do exemplo (API do cliente Java do Kafka: `KafkaConsumer.seek(TopicPartition, long)` e `poll(Duration)`); o controle do offset pelo consumidor: K-DES P58 | "The consumer thus has significant control over this position and can rewind it to re-consume data if need be." |
| `decisao` | "O log só apaga quando vence a retenção que você configurou"; tela "apaga quando vence a retenção" | K-INT P32 | "Instead, you define for how long Kafka should retain your events through a per-topic configuration setting, after which old events will be discarded." |
| `decisao` | tela Fila: "ler apaga a mensagem", "não dá para reler" | R-S P23 | ver `fila` |
| `decisao` | "reprocessar roda tudo de novo, então o antifraude precisa ser idempotente"; tela "reler roda tudo de novo" | K-DES P69 (re-consumir = processar de novo); a conclusão "precisa ser idempotente" é do roteiro, sem fonte direta. Apoio geral: SQS-T P9 | "design your application to handle potential duplicate messages by using idempotent operations, which ensure that processing the same message multiple times will not affect the system’s state." |

Rodapé do vídeo: "Fontes: docs do Apache Kafka 4.4, RabbitMQ e Amazon SQS · app fictício".
