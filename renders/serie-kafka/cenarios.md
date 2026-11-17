# Série Kafka — cenários cena a cena (proposta de 2026-11-15, para validação do dono)

Pedido do dono: "vídeo bem animado" e "pensar em cenários". Base: `serie.md` (pautas e fontes) e
`renders/serie-conceitos/direcao-editorial.md`.

## Mudanças do dono durante a produção (2026-11-15)

- **Celular com notificações** como a vista do cliente: Lottie original (`lottie_celular.py`), na capa de todos os
  episódios e numa cena de volta quando ajuda (ep1 e ep3).
- **Sem cartão de pergunta na abertura:** "começar com uma imagem BEM clara do que estamos tratando". A cena `hook`
  saiu dos quatro episódios; a fala da abertura descreve o que o celular mostra e a notificação muda no tempo da fala.
  As tabelas abaixo são o plano original; o que vale é o `content.pt.json` de cada pasta.

## O cenário da série

Um só mundo nos 4 episódios: **um app de delivery na hora do almoço** (sem marca real). O serviço de **Pedidos**
precisa avisar **Pagamento**, **Restaurante**, **Entregador** e **Notificação**. Cada episódio é um problema desse
app, e o Kafka entra como a resposta. Continuidade: o espectador reconhece os mesmos blocos de um vídeo para outro,
e o selo "Parte N de 4" fecha cada um.

## Como fica "bem animado"

Nenhuma cena de cartão parado, a não ser a pergunta (`hook`). Cada cena tem algo andando, mudando de estado ou
apontando, com tipos que o kit (0.13.0) já renderiza:

| Peça do kit | O que vira na série |
| --- | --- |
| `flow` | serviços como blocos, setas, **fichas andando** ("pedido #123"), estados (rodando, esperando, falhou, parado) |
| `memory` | o **log** do tópico como fita numerada; **ponteiros nomeados** (os offsets de cada consumidor) que andam e voltam |
| `lanes` | as **partições** como raias, com os eventos de cada pedido caindo na raia certa, em ordem |
| `pipeline` | a **fila**: itens entram, o worker pega, o item some |
| `code` | a linha de Java em foco, passo a passo |
| `versus` | a decisão no fim: os dois lados, e o lado certo acende no tempo da fala |

Estilo `editorial`, `safeArea: "shorts"`, sem janela do dono (como os últimos Shorts), rodapé com a fonte
("Docs: Apache Kafka 4.4 · RabbitMQ · Amazon SQS"). Abertura nos primeiros 3 a 5 s com o fluxo já se mexendo e a
pergunta escrita na cena seguinte (direção de 2026-11-07). Fala ~2,5 palavras/s; alvo 38 a 45 s.

---

## Episódio 1 — Por que o Kafka existe?

**Cenário:** meio-dia, o Pedidos chama os quatro serviços um a um. A Notificação cai e o pedido trava.

| # | Cena (peça) | O que se mexe | Fala (rascunho) | Fonte |
| --- | --- | --- | --- | --- |
| 1 | `flow` (capa) | Pedidos no centro; a ficha "pedido #123" vai até cada um dos 4 serviços; a Notificação fica vermelha e o Pedidos passa a "esperando" | "Meio-dia no app de delivery. Cada pedido avisa quatro serviços, um por um." | cenário |
| 2 | `hook` | pergunta escrita | "Um cai, e o pedido trava. Por que o Kafka existe?" | — |
| 3 | `flow` | entra um 5º serviço (Analytics): nova seta tracejada saindo do Pedidos | "E todo serviço novo é mais uma ligação dentro do Pedidos." | cenário |
| 4 | `flow` | Pedidos → tópico `pedidos` → 4 serviços; a ficha vai **uma vez** ao tópico e cada serviço a puxa em tempos diferentes | "Com Kafka, o Pedidos escreve o evento uma vez num tópico. Cada serviço lê no seu ritmo, e o Pedidos não espera ninguém." | K-INT P31–P32 |
| 5 | `code` | `producer.send(new ProducerRecord<>("pedidos", pedidoId, json));` com foco no tópico | "Em Java, é um send." | código do exemplo |
| 6 | `flow` | Notificação cai; o Pedidos segue escrevendo (3 fichas entram no tópico); a Notificação volta e puxa as 3 | "Se a Notificação cai, os eventos esperam no tópico. Ela volta e lê de onde parou." | K-INT P32; K-DES P68 |
| 7 | `versus` | "Direto: simples, acoplado" × "Tópico: desacoplado, um cluster a mais"; os dois acendem, um de cada vez | "O ganho é desacoplar. O custo é operar um cluster, ou pagar um serviço gerenciado." | K-INT P21, P24 |
| 8 | `end_card` (`next`, Parte 1 de 4) | — | "Você ligaria seus serviços direto ou por um tópico?" | — |

---

## Episódio 2 — Fila × log: por que no Kafka a mensagem não some

**Cenário:** o antifraude do app analisa cada pagamento. Às 15h o time descobre um bug na regra que vale desde as 14h.
Dá para analisar de novo?

| # | Cena (peça) | O que se mexe | Fala (rascunho) | Fonte |
| --- | --- | --- | --- | --- |
| 1 | `pipeline` (capa) | pagamentos entram na fila, o antifraude pega, o item some | "O antifraude do app lê cada pagamento de uma fila." | cenário |
| 2 | `hook` | pergunta escrita | "Bug na regra desde as duas. Dá para analisar tudo de novo?" | — |
| 3 | `pipeline` | estágio final "apagada": tudo que foi lido sai da esteira | "Numa fila, ler é apagar. No RabbitMQ e no SQS, a mensagem sai quando o consumidor termina." | R-S P23; SQS-W P22–P23 |
| 4 | `memory` | fita de pagamentos 0…9 que fica; ponteiros "antifraude" e "extrato" andando separados | "No Kafka, o tópico é um log: ler não apaga. Cada consumidor guarda só um número, o offset da próxima mensagem." | K-INT P32; K-DES P68 |
| 5 | `memory` | o ponteiro "antifraude" **volta** para a célula das 14h e anda de novo | "Corrigiu o bug? Volta o offset para as duas e reprocessa." | K-DES P69 |
| 6 | `code` | `consumer.seek(particao, offsetDas14h);` | "Em Java, um seek." | código do exemplo |
| 7 | `versus` | "Fila: some ao ler" × "Log: some pela retenção" | "O log apaga pela retenção que você configurar, não pela leitura. E reprocessar repete o efeito: o antifraude tem que ser idempotente." | K-INT P32; K-DES P69 |
| 8 | `end_card` (Parte 2 de 4) | — | "Você já precisou reprocessar uma fila?" | — |

Liga com o Short de idempotência já publicado (fecho da cena 7).

---

## Episódio 3 — Partição e chave: ordem e escala

**Cenário:** pico do almoço, um consumidor não dá conta. Põem mais três. Agora o "saiu para entrega" do pedido 7 pode
chegar antes do "pago"?

| # | Cena (peça) | O que se mexe | Fala (rascunho) | Fonte |
| --- | --- | --- | --- | --- |
| 1 | `lanes` (capa) | uma raia só, entupida de eventos | "Pico do almoço: um consumidor não dá conta dos pedidos." | cenário |
| 2 | `hook` | pergunta escrita | "Põe mais três. E o pedido sai antes de ser pago?" | — |
| 3 | `flow` | numa fila com 4 consumidores, um evento volta (reentrega) e passa na frente | "Numa fila com vários consumidores, uma reentrega pode trocar a ordem." | R-Q P85 |
| 4 | `flow` | produtor → chave `pedidoId` → partição 0, 1 ou 2; fichas da mesma cor caem sempre na mesma | "No Kafka, o tópico tem partições, e a mesma chave cai sempre na mesma partição." | K-INT P33 |
| 5 | `lanes` | 3 raias; na raia 1, "#7 criado → #7 pago → #7 saiu", em ordem | "Dentro da partição, a ordem é a de escrita." | K-INT P33 |
| 6 | `flow` | 3 partições → 3 consumidores rodando; entra o 4º e fica "parado" | "No grupo, cada partição tem um consumidor por vez. O quarto fica parado." | K-DES P68 |
| 7 | `code` | `new ProducerRecord<>("pedidos", pedidoId, evento)` com `pedidoId` aceso | "A chave é o pedidoId." | código do exemplo |
| 8 | `versus` | "Ordem: por chave, não no tópico" × "Paralelismo: até o nº de partições" | "Ordem vale por chave. E as partições são o teto de consumidores do grupo." | K-INT P33; K-DES P68 |
| 9 | `end_card` (Parte 3 de 4) | — | "Que chave você usaria nos seus eventos?" | — |

---

## Episódio 4 — Kafka, RabbitMQ ou SQS: qual usar?

**Cenário:** dois trabalhos no mesmo app: redimensionar a foto do prato que o restaurante enviou, e avisar quatro
serviços que o pedido foi pago.

| # | Cena (peça) | O que se mexe | Fala (rascunho) | Fonte |
| --- | --- | --- | --- | --- |
| 1 | `flow` (capa) | duas fichas saem do app: "foto do prato" e "pedido pago" | "Dois trabalhos no app: redimensionar a foto do prato e avisar que o pedido foi pago." | cenário |
| 2 | `hook` | pergunta escrita | "Kafka, RabbitMQ ou SQS: qual é o melhor?" | — |
| 3 | `pipeline` | foto → fila → 3 workers → pronta (some) | "A foto é tarefa: um worker faz uma vez, e acabou. Isso é fila. O guia do SQS usa esse exemplo." | SQS-T P17–P18 |
| 4 | `versus` | "RabbitMQ: você opera o servidor" × "SQS: a AWS opera, escala sozinha, guarda até 14 dias" | "No RabbitMQ, você roda o servidor. No SQS, a AWS roda, escala sozinha e guarda por até catorze dias." | R-Q P5; SQS-W P11, P25 |
| 5 | `memory` | "pedido pago" no log; 4 ponteiros, um por serviço, andando em ritmos diferentes | "O pedido pago é histórico: quatro serviços leem no seu ritmo e podem reler. Isso é log, o Kafka." | K-INT P32; K-DES P68 |
| 6 | `flow` | RabbitMQ ganha uma seta para "streams"; Kafka ganha uma para "share groups" | "E a fronteira borrou: o RabbitMQ ganhou streams, e o Kafka 4, grupos que funcionam como fila." | R-S P5, P15; K-DES P118–P121 |
| 7 | `versus` | "Tarefa que some → fila" × "Histórico que vários releem → log" | "Então o melhor depende: tarefa que some, fila. Histórico que vários releem, log." | síntese das fontes acima |
| 8 | `end_card` (`follow`, Parte 4 de 4) | — | "Qual você usa no trabalho?" | — |

---

## Música e som (planejado antes da voz)

- Uma faixa para a série inteira: `ytal-spirit-of-fire` (a mesma de idempotência e consistent hashing; calma, sem
  voz, 608 s). Fundo baixo desde o 1º quadro; silêncio curto na virada (cena do Kafka entrando); fundo saindo na
  frase de decisão (`versus`); volta no convite. Instagram sem faixa (licença só no YouTube).
- `vp short juntar` ainda não mistura música: fica "música planejada, mistura pendente".
- SFX do kit (CC0) nos cortes e quando a ficha chega ao tópico, se você quiser.

## O que muda em relação às regras da série "eu medi"

- Sem `medicao.json` e sem número nosso; o único número na tela é o "14 dias" do SQS (fonte SQS-W P25) e os índices
  didáticos do log.
- A ordem do gate continua: você assiste a cada um e aprova; nada é agendado.
