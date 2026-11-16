# Fontes — episódio 3, "Partição e chave: ordem e escala" (`short-kafka-particao-pt`)

Fontes baixadas em 2026-11-15 (`../fontes/raw/baixado-em.txt`), texto numerado em `../fontes/`. Ids como em
`../serie.md`. Pedidos (#3, #7, #9), os quatro consumidores e as três partições são exemplo didático; não há número
nosso nem medição.

| Cena | Fala ou tela | Fonte | Trecho literal |
| --- | --- | --- | --- |
| `abertura` (capa) | Celular: "Saiu para entrega" antes de "Pagamento aprovado", "fora de ordem"; fala "Pico do almoço, quatro consumidores na fila. E no celular do cliente, o pedido sai antes de ser pago." | cenário, sustentado por R-Q P85 (cena `fila`) | — (ilustração do risco da fila; o mecanismo vem na cena `fila`) |
| `fila` | "Numa fila com vários consumidores, uma reentrega pode trocar a ordem: o pago volta, e o saiu passa na frente." Tela: o Consumidor 1 falha, a ficha "#7 pago" volta à fila e a "#7 saiu" vai ao Consumidor 2 | R-Q P85 (RabbitMQ, Queues) | "Multiple active consumers on the same queue: the broker still dequeues in FIFO, but any redelivery can change order. Redelivery happens when consumers negatively acknowledge with requeue or a channel/session closes with unacked messages." |
| `chave` | "No Kafka, o tópico tem partições, e a mesma chave cai sempre na mesma partição." Tela: produtor com a chave pedidoId; as fichas do #7 vão sempre à Partição 1 | K-INT P33 | "Topics are partitioned , meaning a topic is spread over a number of “buckets” located on different Kafka brokers." … "Events with the same event key (e.g., a customer or vehicle ID) are written to the same partition" |
| `ordem` | "Quem lê a partição recebe na ordem em que foi escrito." Tela: raias Part. 0/1/2, "#7 criado → #7 pago → #7 saiu" na Part. 1 | K-INT P33 | "Kafka guarantees that any consumer of a given topic-partition will always read that partition’s events in exactly the same order as they were written." |
| `grupo` | "No grupo, cada partição tem um consumidor por vez. O quarto fica parado." Tela: Partição 0/1/2 → Consumidor 1/2/3 rodando; Consumidor 4 "sem partição", parado | K-DES P68 | "Our topic is divided into a set of totally ordered partitions, each of which is consumed by exactly one consumer within each subscribing consumer group at any given time." |
| `codigo` | "Em Java, a chave é o pedidoId, o segundo argumento do ProducerRecord." Tela: `new ProducerRecord<>("pedidos", pedidoId, json)` | código do exemplo; K-INT P27 (o evento tem chave) | "Conceptually, an event has a key, value, timestamp, and optional metadata headers." |
| `cliente` | "E no celular do cliente, os avisos voltam a chegar na ordem certa." Tela: criado → pago → saiu | consequência de K-INT P33 (mesma chave, mesma partição, leitura em ordem) | ver `chave` e `ordem` |
| `decisao` | "A ordem vale por chave. E as partições limitam os consumidores do grupo." Tela: "Ordem: vale por chave / não no tópico inteiro"; "Paralelismo: até o número de partições / consumidor a mais fica parado" | K-INT P33; K-DES P68; K-DES P117 | P33: "any consumer of a given topic-partition will always read that partition’s events in exactly the same order as they were written." P117: "The way that consumer groups assign partitions to members of the group gives a powerful combination of ordering and scalability." |

## Notas

- **O 4º consumidor parado** (cenas `grupo` e `decisao`) não está escrito com essas palavras nas fontes: é
  consequência de K-DES P68. Se cada partição é lida por exatamente um consumidor do grupo de cada vez, com três
  partições só três consumidores do grupo recebem partição, e o quarto fica sem nada para ler. O mesmo vale para
  "as partições limitam os consumidores do grupo".
- **"Não no tópico inteiro"** (cena `decisao`): K-INT P33 garante a ordem por partição ("that partition’s events");
  não há garantia de ordem entre partições diferentes nas fontes. A tela diz o limite sem afirmar além disso.
- **A reentrega** (cena `fila`) é o caso da fila do RabbitMQ (R-Q P85); a fala diz "numa fila" porque o exemplo é
  uma fila comum, e o rodapé cita o RabbitMQ. A falha do Consumidor 1 na tela corresponde a "a channel/session
  closes with unacked messages".
- Sem cena de pergunta: a abertura é só o celular (pedido do dono em 2026-11-15). A ordem errada no celular (`abertura`) é o risco da fila, não do Kafka com chave: a fala da cena `fila` mostra a
  causa, e as cenas `chave`, `ordem` e `cliente` mostram a correção.
