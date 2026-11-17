# Série Kafka (Shorts técnicos, pt) — proposta de 2026-11-15

Pedido do dono em 2026-11-15: uma pequena série de Shorts sobre Kafka, **sem medição**, explicando direto com
exemplo e animação ("a maioria dos vídeos não coloca medição, só exemplifica"). Perguntas que a série responde:
**por que o Kafka existe, como ele se compara às alternativas e qual escolher**. Segue a direção editorial da série
de conceitos (`renders/serie-conceitos/direcao-editorial.md`): abertura em 3 ou 4 quadros, impacto em System Design
mostrado em blocos e setas, linguagem explícita (código do cliente Java na tela), 35 a 45 s, funil `topo`,
objetivo `explicar`. Busca: "kafka" ~5,6 mil/mês no Brasil (vidIQ, `docs/pesquisa/temas-serie-conceitos-vidiq-2026-11-03.md`).

**Sem medição:** nenhum número de tempo ou vazão nosso. Os números que aparecem são das fontes (ex.: retenção do
SQS) ou valores de exemplo ditos como exemplo. O `vp medicao` não se aplica; o rastreio de cada número fica no
`fontes.md` de cada episódio.

## Fontes primárias (baixadas em 2026-11-15, texto numerado em `fontes/`)

| Id | Documento | Arquivo |
| --- | --- | --- |
| K-DES | Apache Kafka 4.4, Design (`kafka.apache.org/44/design/design/`) | `fontes/kafka-design.txt` |
| K-INT | Apache Kafka 4.4, Introduction (`kafka.apache.org/44/getting-started/introduction/`) | `fontes/kafka-introduction-44.txt` |
| K-USE | Apache Kafka 4.4, Use cases | `fontes/kafka-uses-44.txt` |
| R-Q | RabbitMQ, Queues (`rabbitmq.com/docs/queues`) | `fontes/rabbitmq-queues.txt` |
| R-S | RabbitMQ, Streams (`rabbitmq.com/docs/streams`) | `fontes/rabbitmq-streams.txt` |
| SQS-W | Amazon SQS Developer Guide, What is Amazon SQS | `fontes/sqs-welcome.txt` |
| SQS-T | Amazon SQS Developer Guide, Queue types | `fontes/sqs-queue-types.txt` |
| PUL | Apache Pulsar, Overview | `fontes/pulsar-overview.txt` |

Redis Streams foi baixado (`fontes/redis-streams.txt`), mas a página veio poluída; fica fora da série.

## Episódio 1 — Por que o Kafka existe?

- **Pergunta:** que problema o Kafka resolve que um sistema chamando o outro não resolve?
- **Abertura em quadros:** (1) pedidos → pagamentos; (2) entram estoque, e-mail, analytics: setas se cruzam;
  (3) a teia inteira, uma caixa cai e as setas ficam vermelhas; (4) pergunta escrita: "Por que o Kafka existe?"
- **Mecanismo:** o produtor escreve o evento uma vez num tópico; cada consumidor lê no próprio ritmo; produtor e
  consumidor não se conhecem e o produtor nunca espera o consumidor (K-INT P31). Evento = chave, valor, horário
  (K-INT P27–P30). Código: `producer.send(new ProducerRecord<>("pedidos", clienteId, pedidoJson))`.
- **Motivação dos autores:** plataforma unificada para os fluxos de dados em tempo real de uma empresa grande
  (K-DES P5): alta vazão (P6), grandes acúmulos vindos de cargas offline (P7), baixa latência (P8), tolerância a
  falha de máquina (P10); desenho "mais parecido com o log de um banco de dados que com um sistema de mensageria
  tradicional" (P11).

| Item | Definição | Situação |
| --- | --- | --- |
| Aplicação | Loja: serviço de pedidos que precisa avisar pagamentos, estoque, e-mail e analytics | Cenário didático |
| Decisão de System Design | Integração ponto a ponto × publicar o evento num log central (tópico) | Explícita |
| Benefício e limite | Benefício: produtor desacoplado, consumidor novo sem mexer no produtor (K-INT P31–P32). Limite: um cluster de brokers a mais para operar, ou serviço gerenciado (K-INT P21, P24) | Com fonte |
| Explicação visual | Teia de setas → cada serviço com uma seta só até o tópico; um consumidor cai e o produtor segue escrevendo; ele volta e lê de onde parou | A detalhar no plano |

## Episódio 2 — Fila × log: por que no Kafka a mensagem não some

- **Pergunta:** o que acontece com a mensagem depois que alguém lê?
- **Mecanismo:** numa fila, consumir apaga — RabbitMQ: as filas "convergem para vazio" e o consumo é destrutivo
  (R-S P23, P27); SQS: o consumidor apaga a mensagem depois de processar (SQS-W P22–P23). No Kafka, ler não apaga:
  o tópico guarda pelo tempo configurado (K-INT P32), e o consumidor só guarda um número, o offset da próxima
  mensagem (K-DES P68). Código: `consumer.seek(particao, offset)`.
- **Consequência:** dois serviços leem os mesmos eventos sem uma fila por consumidor (R-S P21 descreve o custo da
  fila por consumidor); um bug corrigido reprocessa voltando o offset (K-DES P69).

| Item | Definição | Situação |
| --- | --- | --- |
| Aplicação | Serviço de antifraude com bug descoberto depois de processar um dia de pagamentos | Cenário didático |
| Decisão de System Design | Fila (consumo destrutivo) × log com retenção e offset por consumidor | Explícita |
| Benefício e limite | Benefício: reprocessar e vários leitores independentes (K-DES P69, R-S P21). Limite: o log não apaga por mensagem lida — apaga pela retenção (K-INT P32); voltar o offset viola o contrato de fila (K-DES P69) e reprocessa o que já tinha passado | Com fonte |
| Explicação visual | Fila: mensagens saem e somem. Log: mensagens ficam numeradas 0,1,2…; dois ponteiros (antifraude, analytics) andam separados; o ponteiro do antifraude volta | A detalhar no plano |

## Episódio 3 — Partição e chave: ordem e escala

- **Pergunta:** como o Kafka divide o trabalho entre consumidores sem embaralhar os pedidos de um cliente?
- **Mecanismo:** o tópico é dividido em partições em brokers diferentes (K-INT P33); evento com a mesma chave vai
  para a mesma partição e é lido na ordem em que foi escrito (K-INT P33); cada partição é lida por exatamente um
  consumidor de cada grupo (K-DES P68). Código: a chave `clienteId` no `ProducerRecord`.
- **Consequência:** escalar = mais partições e mais consumidores no grupo; a ordem vale dentro da partição, não no
  tópico inteiro.

| Item | Definição | Situação |
| --- | --- | --- |
| Aplicação | Pedidos de vários clientes: "criado", "pago", "enviado" do mesmo cliente não podem inverter | Cenário didático |
| Decisão de System Design | Escolher a chave do evento e o número de partições | Explícita |
| Benefício e limite | Benefício: paralelismo entre partições com ordem por chave (K-INT P33, K-DES P68). Limite: num grupo, uma partição tem um consumidor por vez, então consumidor além do número de partições fica sem partição (consequência de K-DES P68; conferir a frase na fala) | Com fonte; limite inferido, revisar |
| Explicação visual | 3 partições como trilhos; eventos coloridos por cliente caem sempre no mesmo trilho; 3 consumidores, um por trilho; um 4º consumidor entra e fica parado | A detalhar no plano |

## Episódio 4 — Kafka, RabbitMQ ou SQS: qual usar?

- **Pergunta:** qual é o melhor? Resposta da série: depende do padrão da mensagem, e cada documentação diz para
  que serve. Sem ranking.
- **Cada um pela própria fonte:**
  - **RabbitMQ (fila):** FIFO clássico, desenhado para convergir para vazio (R-Q P5, R-S P27); distribuir tarefas.
    Ele também tem streams, que "complementam, não substituem" as filas (R-S P15).
  - **Amazon SQS:** fila gerenciada que escala sem provisionar (SQS-W P11); standard = pelo menos uma vez e ordem
    de melhor esforço; FIFO = ordem dentro do grupo de mensagens (SQS-T P9, P10, P15); retenção padrão de 4 dias,
    máximo 14 (SQS-W P25); uso citado: tirar trabalho pesado da requisição e repartir tarefas entre workers
    (SQS-T P17–P18).
  - **Kafka:** guardar e reler fluxos de eventos pelo tempo que quiser, com vários consumidores e processamento
    de fluxo (K-INT P17–P20, P32).
  - **Pulsar (menção):** multi-tenant, geo-replicação nativa, mais de um milhão de tópicos (PUL P5, P8, P10).
- **Fecho:** tarefa que some depois de feita → fila; histórico que vários leem e releem → log. Convite: "qual você
  usa no trabalho?"

| Item | Definição | Situação |
| --- | --- | --- |
| Aplicação | Mesma loja: redimensionar imagens enviadas (tarefa) × eventos de pedido lidos por 4 serviços (histórico) | Cenário didático; o primeiro caso é o exemplo do próprio SQS-T P17 |
| Decisão de System Design | Escolher fila ou log pelo padrão de consumo | Explícita |
| Benefício e limite | Por opção, só o que a própria documentação diz; "melhor" é sempre "melhor para quê" | Com fonte |
| Explicação visual | Duas colunas: tarefa entra na fila → worker → some; evento entra no log → 4 ponteiros; as quatro tecnologias encaixam numa coluna ou na outra (RabbitMQ aparece nas duas, por causa dos streams) | A detalhar no plano |

## Episódio 5 (opcional) — O Kafka 4 também virou fila

Share groups: consumidores cooperam numa mesma partição, podem passar do número de partições e as tentativas de
entrega são contadas (K-DES P118–P123), com trava por tempo em cada registro (P126). Fecha o arco do episódio 4.
Fica para depois dos quatro, se o dono quiser.

## Pendências comuns (antes da voz)

- Plano de animação por episódio, com a seção "Música" (faixa do catálogo; mistura no `juntar` ainda pendente).
- Janela do dono (pele com `origem.json` em `needs_review`): seguir o que os Shorts recentes fizeram.
- `fontes.md` de cada episódio com o trecho literal de cada afirmação.
- Gates e agendamento são do dono.
