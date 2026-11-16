# Episódio 4 — Kafka, RabbitMQ ou SQS: qual usar? — fontes por fala e tela

Ids e arquivos em `../serie.md` (texto numerado em `../fontes/`, baixado em 2026-11-15). Cenário (app de delivery,
foto do prato, pedido #123, os quatro leitores Loja/Aviso/Rota/Dados e os números das células do log) é fictício e
didático; não é fato. Nenhum número nosso: o único número de fato é o "até 14 dias" da AWS.

| Cena | Fala ou tela | Fonte | Trecho literal |
| --- | --- | --- | --- |
| `abertura` (capa, sem pergunta) | "No app, a foto do prato precisa ser redimensionada, e o pedido pago avisa quatro serviços. Os candidatos: Kafka, RabbitMQ e SQS." / celular: "Foto do prato enviada" (quadro 0), "Pagamento aprovado" (desce em 3,7 s), "Kafka · RabbitMQ · SQS" (5,5 s) | cenário | — |
| `tarefa` | "A foto é tarefa: um worker faz uma vez, e acabou. Isso é fila." / esteira foto → fila → workers → pronta (a fala não cita a fonte; o rodapé mostra) | SQS-T P17 | "Allow users to upload media quickly while you process tasks like resizing or encoding in the background" |
| `tarefa` | "e acabou" / estágio "sai da fila" | SQS-W P23 | "The consumer (Component 2) deletes message A from the queue to prevent the message from being received and processed again" |
| `filas` | "A fila do RabbitMQ é feita para esvaziar" / tela "feita para esvaziar" | R-S P27 | "Most RabbitMQ queues are designed to converge towards the empty state" |
| `filas` | tela "fila FIFO" (RabbitMQ) | R-Q P5 | "Messages are enqueued and dequeued (delivered to consumers) in a (FIFO (\"first in, first out\") manner." |
| `filas` | "O SQS fica na AWS" / tela "hospedada na AWS" | SQS-W P6 | "Amazon Simple Queue Service (Amazon SQS) offers a secure, durable, and available hosted queue" |
| `filas` | "escala sozinho" / tela "escala sem provisionar" | SQS-W P11 | "scaling transparently to handle any load increases or spikes without any provisioning instructions" |
| `filas` | "guarda até catorze dias" / tela "guarda até 14 dias" | SQS-W P25 | "The default message retention period is 4 days. However, you can set the message retention period to a value from 60 seconds to 1,209,600 seconds (14 days)" |
| `historico` | "quatro serviços leem no seu ritmo e podem reler" / fita com quatro ponteiros | K-INT P32 | "a topic can have zero, one, or many producers that write events to it, as well as zero, one, or many consumers that subscribe to these events. Events in a topic can be read as often as needed-unlike traditional messaging systems, events are not deleted after consumption." |
| `historico` | ponteiro = posição do leitor (offset) | K-DES P68 | "the position of a consumer in each partition is just a single integer, the offset of the next message to consume" |
| `historico` | "no seu ritmo" | K-INT P31 | "producers and consumers are fully decoupled and agnostic of each other" |
| `fronteira` | "o RabbitMQ tem streams, que se releem" / tela "Streams · log que se relê" | R-S P6 | "Streams model an append-only log of messages that can be repeatedly read until they expire." |
| `fronteira` | aresta "também" (streams ao lado das filas, não no lugar) | R-S P15 | "streams were not introduced to replace queues but to complement them" |
| `fronteira` | "e o Kafka tem share groups" | K-DES P118 | "Share groups are another type of group, existing alongside traditional consumer groups." |
| `fronteira` | tela "Share groups · dividem a partição" | K-DES P120 | "The consumers in a share group cooperatively consume records, and partitions may be assigned to multiple consumers." |
| `fronteira` | (apoio, não dito) mais consumidores que partições | K-DES P121 | "The number of consumers in a share group can exceed the number of partitions in a topic." |
| `decisao` | "Então depende: tarefa que some, fila. Histórico que vários releem, log." / tela Fila (RabbitMQ, SQS) × Log (Kafka) | síntese de SQS-T P17, R-S P23/P27, K-INT P32 | ver linhas acima; é a leitura do canal, não frase de uma fonte |
| `fecho` | "E você, qual desses três usa hoje no trabalho?" | convite | — |

Conferências pedidas: SQS FIFO = ordem dentro do grupo de mensagens (SQS-T P15: "FIFO queues ensure that you receive
messages in the order they are sent within each message group") — **não entrou na fala nem na tela** deste episódio,
para caber no tempo; se entrar numa versão, dizer "ordem dentro do grupo", nunca "ordem garantida" no geral.
RabbitMQ streams complementam e não substituem as filas (R-S P15): conferido, na aresta "também".
Share groups podem ter mais consumidores que partições (K-DES P121): conferido, fica como apoio, não dito.
