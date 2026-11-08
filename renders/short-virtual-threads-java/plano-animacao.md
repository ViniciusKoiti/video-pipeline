# Virtual threads em Java: plano de animação

Plano feito antes de voz e render (direção editorial de 2026-11-01; pauta aprovada em 2026-11-03,
`data/episodes/short-virtual-threads-java-pt/pauta.md`). Forma: `flow` do motion-kit para o mecanismo (a fila na
frente do pool, as virtuais sem fila, a fila que reaparece na frente das conexões), `code` para a linha que muda,
`versus` e `categories` para os números medidos. Os tempos dos estados nas cenas de fluxo são **ilustração
sincronizada à fala**, não tempos da medição; os números da tela vêm só de `medicao.json`. As latências são
**simuladas** (`Thread.sleep(100)`), e a tela diz isso no rodapé.

## Controle obrigatório (quadro da direção editorial)

| Item | Definido para este tema | Antes da voz/render | Depois do render |
| --- | --- | --- | --- |
| Aplicação | Serviço de pedidos em Java: requisições HTTP → pool de threads (ou virtual threads) → chamada bloqueante (banco, simulada por `Thread.sleep(100)`) → pool de 50 conexões (`Semaphore`) | Cenário na pauta e nas cenas `plataforma`, `virtual`, `conexoes` | Nós `Requisições`, `Thread Java`, `Thread do SO`, `Pool de 200 threads`, `Virtual threads`, `Conexões`, `Banco` reconhecíveis (conferido em 2026-11-04 nos quadros do `review` e do `final.pt.mp4`/`final.en.mp4`) |
| Decisão de System Design | Trocar o pool fixo de threads por uma virtual thread por requisição **e dimensionar o pool de conexões, que passa a ser o limite** | Gancho (onde o gargalo vai parar?), `codigo` (a linha que muda), `conexoes` e fecho (qual limite dimensionar) | Relação "tirou o limite de threads, o gargalo foi para as conexões" dita na fala e vista nos fluxos (conferido em 2026-11-04 nos quadros do `review` e do `final.pt.mp4`/`final.en.mp4`) |
| Benefício e limite | Benefício: tempo para atender as 10 mil esperando I/O, pool de 200 × virtual (medido). Limite: com 50 conexões o tempo volta a depender delas (medido); exemplo com espera simulada, sem CPU, sem rede real | Fontes: `fontes.md` (V1–V8, E1–E2); medição: `demo/resultado.txt` | Afirmações conferidas contra `medicao.json` e a fala (conferido em 2026-11-04 nos quadros do `review` e do `final.pt.mp4`/`final.en.mp4`) |
| Explicação visual | `threads`: o que é uma thread e por que a do sistema é o recurso caro; `plataforma`: requisições → fila → pool de 200; só 200 nós ativos, o resto espera. `virtual`: requisições → uma virtual thread cada → I/O, sem fila. `conexoes`: virtual threads → `Semaphore` (50) → banco, a fila reaparece | Sequência abaixo, ligada à fala | Quadros antes/durante/depois abertos e conferidos (conferido em 2026-11-04 nos quadros do `review` e do `final.pt.mp4`/`final.en.mp4`) |

## Cenas

| Cena (`id`) / trecho da fala | Estado inicial | Blocos e conexões | Ação visível | Estado final | Fonte |
| --- | --- | --- | --- | --- | --- |
| `gancho` (hook, capa) / "Dez mil requisições esperando I/O em Java: onde vai parar o gargalo?" | Pergunta na capa | Texto com "Java" e "gargalo" em destaque, kicker "Java · JDK 25" | Nomear a linguagem, o cenário e a pergunta | Expectativa: o que muda e onde o limite reaparece | Pauta |
| `threads` (flow) / "Uma thread é a linha de execução de uma requisição, e em Java ela segura uma thread do sistema operacional, que é cara, mesmo quando só espera." | Tudo `idle` | Requisição → Thread Java (`atende`) → Thread do SO (`segura uma`, sublabel "cara: são poucas") e Thread Java → Chamada bloqueante (`espera`) | A requisição entra; a Thread Java e a Thread do SO ficam `running`; quando a chamada bloqueante começa, a Thread Java e a Thread do SO ficam `waiting` (presas esperando) | O espectador vê que esperar I/O não solta a thread do sistema, que é o recurso caro | T1, T2, V1 |
| `plataforma` (flow) / "Por isso o pool limita em duzentas: só duzentas requisições esperam por vez, e o resto fica na fila." | Tudo `idle` | Requisições (`10.000`) → Pool (`200 threads`) → Chamada bloqueante (`espera 100 ms`); a aresta Requisições→Pool rotulada "fila" | Um dado `requisição` entra; o pool fica `running`; a espera fica `running` por ~3 s; a fila continua cheia | O limite é o pool: a fila está na frente dele | V1, V2, E2; demo (constantes 200, 100 ms) |
| `codigo` (code, passos) / "Trocar o pool por uma virtual thread por requisição é uma linha." | Código inteiro | Linhas 1–2: `newFixedThreadPool(200)`; 4–5: `newVirtualThreadPerTaskExecutor()` | Passo 1 acende o pool; passo 2 acende a linha das virtuais | O mesmo `submit`, outro executor | E1, E2; `Demo.java` |
| `virtual` (flow) / "A virtual thread é gerenciada pela JVM e não segura uma thread do sistema enquanto espera, então as dez mil esperam juntas." | Tudo `idle` | Requisições → Virtual threads (`uma cada`) → Chamada bloqueante (`esperam juntas`); Virtual threads → Threads do SO (tracejada, `só ao rodar`) | Os dados entram juntos; as virtuais e a Thread do SO ficam `running` por um instante; ao começar a espera, a Thread do SO volta a `idle` (livre) e a chamada bloqueante fica `running` com todas | A espera não prende a thread do sistema; sem fila | T3, T4, T5, V3, V4, V5, E1 |
| `medido` (categories) / "Pool de duzentas: A. Virtuais: B. Virtuais com cinquenta conexões: C." | Barras | Pool de 200 threads, virtuais, virtuais com 50 conexões (s) | A barra das virtuais com 50 conexões em destaque | O ganho e o limite, medidos | Medição (medianas) |
| `conexoes` (flow, turn) / "Mas se o banco aceita cinquenta conexões, a fila reaparece nelas." | Tudo `idle` | Virtual threads → Conexões (`Semaphore 50`) → Banco; rótulo "fila" na aresta Virtual threads→Conexões | Os dados chegam juntos; só cinquenta passam por vez; o nó Conexões fica `running` o tempo todo e o Banco também | O gargalo mudou de lugar: threads → conexões | V6; medição (C) |
| `fecho` (end_card) / "O gargalo saiu das threads e foi para as conexões. Qual limite você dimensionaria?" | Último quadro | Pergunta final | Convite | Decisão de System Design devolvida ao espectador | Pedido editorial |

## Duração

A pauta previa 35 a 45 s; o dono pediu (2026-11-04) que o vídeo **explique o que são threads**, não só mostre
resultados. A cena `threads` e a explicação da virtual thread acrescentam cerca de 10 s: alvo de 50 a 55 s. O
modo `cpu` da pauta fica de fora.

## Pausas planejadas na fala

- `fecho`: uma pausa de cerca de 1 s entre a afirmação e a pergunta, dada pelo ponto final (tempo de o espectador
  pensar no próprio serviço). Fica como está.
- Nenhuma outra pausa de 0,5 s ou mais dentro de uma fala.

## Pontos a conferir na revisão

- `plataforma`: a fila precisa estar visível na aresta e o pool aceso por toda a cena; sem sugerir um tempo medido.
- `virtual`: não pode haver rótulo de fila; todas as virtuais ficam acesas juntas.
- `conexoes`: a fila está entre as virtuais e as conexões (não na frente de um pool de threads).
- Rodapé: "espera simulada (Thread.sleep 100 ms)", JDK, CPU, data e 15 rodadas.
- Fora deste plano: janela do dono (`host`) e efeitos de cena.
