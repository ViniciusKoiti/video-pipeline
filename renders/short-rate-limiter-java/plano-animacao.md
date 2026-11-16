# Rate limiter em Java: plano de animação e narração

**Pauta:** `data/episodes/short-rate-limiter-java-pt/pauta.md` (aprovada em 2026-11-03). **Roteiro e lição:**
`roteiro.md`. **Fontes:** `fontes.md`. **Medição:** `demo/resultado.txt` (Java 25.0.5, 15 rodadas por modo).
Nada agendado nem publicado. Vertical 1080×1920, `safeArea: shorts`, estilo editorial; diagramas de fluxo do kit
(`flow`), originais, sem Lottie, host nem assets externos. Os valores de enchimento e capacidade são os da demo.
Estados do motor (`running`, `waiting`, `failed`, `done`) não são estados do limitador.

## 1. Abertura em quadros (direção de 2026-11-07) e capa

A cena `situacao` é a abertura em três quadros de caixas e setas, sem personagem desenhado: (1) o robô aparece com
"1000 de uma vez" e a seta para o serviço de trás, (2) a rajada chega ao serviço, (3) os cinco clientes normais passam a
esperar atrás dela. O título da cena é a pergunta, escrita na tela desde o primeiro quadro: "E a requisição 101?". O
primeiro quadro (`cover: true`) é o da cena `situacao`: pergunta, robô, clientes e serviço de trás.

## 2. Trechos da fala e cenas (explicação)

| Cena | Trecho da fala | Estado inicial | Blocos e conexões | Ação visível | Estado final | Fonte |
| --- | --- | --- | --- | --- | --- | --- |
| `situacao` | "O que acontece com a requisição 101 quando um robô dispara mil de uma vez?" | Robô, 5 clientes, serviço de trás (10 vagas), tudo parado | Robô → serviço ("rajada"); Clientes → serviço ("normais"); seta = requisição | Ficha de rajada sai do robô, o serviço fica ocupado, os clientes passam a esperar | Clientes `waiting`; pergunta aberta no título | D1 cenário |
| `balde` | "O token bucket ganha vinte fichas por segundo, até cem, e cada requisição gasta uma." | Balde cheio, "até 100 fichas" | Torneira → Balde ("20 por segundo"); Balde → Serviço ("1 ficha por requisição") | Fichas descem da torneira ao balde; uma requisição leva uma ficha ao passar | Balde com regra: enche a taxa fixa, teto, gasta uma por requisição | F2 §3; parâmetros: D1 |
| `recusa` | "Sem ficha vem o erro quatrocentos e vinte e nove, sem chamar o serviço, então a rajada passa só até o tamanho do balde." | Balde "0 fichas", serviço sem ser chamado | Robô → Balde ("nº 101"); Balde → Robô ("429", completion); Balde ⇢ Serviço (tracejado, "bloqueado") | A 101ª requisição chega, volta como 429 e nada vai ao serviço | Robô `failed`; serviço intacto; "100 passam" no balde | F1 §4; F2 §3; D1 (`robo_aceitas=100`) |
| `medido` | "Na simulação, os clientes normais foram de quase três segundos para 51 milissegundos." | Dois modos, sem e com limite | Sem limite → Clientes ("2,9 s"); Com limite → Clientes ("51 ms") | A ficha "2,9 s" vai primeiro e fica pesada (`failed`), depois a "51 ms" chega leve (`done`) | Mediana: 2867 ms × 51 ms | D1 `normais_mediana_ms` |
| `limite` | "O robô levou novecentos erros, e um pico legítimo maior que o balde levaria o mesmo: taxa e tamanho do balde são a decisão." | Balde "0 fichas" | Robô → Balde ("900 recusas"); Pico legítimo (hipótese) → Balde; Balde → Pico ("429", tracejado) | Primeiro o robô recebe a recusa; depois a seta tracejada mostra o pico hipotético recebendo o mesmo | Limite: o balde recusa qualquer pico maior que ele; decisão: taxa e tamanho | D1 `robo_recusadas`; consequência de F2 |
| `fecho` | "Qual tamanho de balde você escolheria para a sua API?" | — | — | Convite (cartão do kit, `follow`) | Pergunta de decisão | pauta |

Duração estimada da fala (2,2 palavras/s): pt ≈ 47 s, en ≈ 48 s (alvo da pauta: 35 a 45 s; passa por pouco, registrado em `roteiro.md`). Os tempos finais vêm dos WAVs.
O ramo "pico legítimo" é hipótese marcada no próprio nó ("hipótese, não medido"): nenhum número na tela.

## 3. Sequência de impacto no System Design

1. **Aplicação:** API de busca com um limitador por cliente na entrada, antes do serviço de trás de capacidade fixa
   (cenas `situacao` e `balde`).
2. **Decisão:** a taxa de enchimento (20 por segundo) e o tamanho do balde (100) de cada cliente (cenas `balde`, `limite`, fecho).
3. **Benefício medido:** mediana dos clientes normais de 2867 ms para 51 ms durante a rajada; o serviço atende 400
   requisições em vez de 1300 (cena `medido`; só a mediana vai à tela).
4. **Limite:** 900 das 1000 requisições do robô viram 429; um pico legítimo maior que o balde teria o mesmo destino
   (consequência do mecanismo, dita no condicional; não medida) (cenas `recusa`, `limite`).
5. **Lacuna declarada:** simulação com `Thread.sleep`, sem rede, sem banco, sem `Retry-After` nem retry do robô.

## 4. Quadro de controle obrigatório (direção editorial)

| Item | Antes da voz/render | Depois do render |
| --- | --- | --- |
| Aplicação | API com limitador por cliente antes do serviço de trás; robô e 5 clientes (`situacao`, `balde`) | a conferir nos quadros |
| Decisão de System Design | taxa e tamanho do balde por cliente; pergunta na tela e no fecho (`situacao`, `limite`, `fecho`) | a conferir |
| Benefício e limite | 2867 → 51 ms; 900 recusas; pico legítimo como consequência, sem número (`medicao.json`, 15 rodadas) | a conferir; parâmetros fixos e simulação |
| Explicação visual | fichas descendo ao balde e gastas por requisição; 101ª recusada sem tocar o serviço; fichas "2,9 s" e "51 ms"; robô e pico hipotético recusados | a conferir nos quadros de início, leitura e fim |

Lacunas antes da voz: nenhuma. Lição dita na fala das cenas `recusa` (rajada passa só até o tamanho do balde) e
`limite` (preço e decisão).

## 5. Música (planejada; mistura pendente)

- **Divergência registrada:** a pauta (2026-11-03) diz "Sem música"; o pedido do dono de 2026-11-05 torna a trilha
  obrigatória em todo Short de conceito e só admite "sem música" com motivo escrito. Como a pauta não dá motivo,
  segui o pedido mais recente. Se o dono preferir sem música, basta ignorar esta seção.
- **Faixa:** `ytal-spirit-of-fire` ("Spirit of Fire", `data/music/catalog.json`: calmo, intensidade 3, sem vocal,
  608 s, dura mais que o vídeo), a mesma da idempotência e do consistent hashing. Licença: YouTube Audio Library,
  só no YouTube.
- **Plano (por cena):**
  - `situacao`: fundo baixo desde o primeiro quadro.
  - `balde`: fundo baixo, sem competir com a leitura da regra.
  - `recusa`: fundo baixo (virada: a 101ª recusada).
  - `medido`: sem música, para o número medido aparecer limpo.
  - `limite`: sem música (resultado e custo).
  - `fecho`: fundo baixo volta e sai no último quadro.
- **Instagram:** sai sem a faixa (licença só do YouTube).
- **Mistura:** `vp short juntar` ainda não mistura música. Fica registrado como `música planejada, mistura pendente`;
  não declarar o vídeo "com música" antes da mistura. O `music.json` não foi escrito (a mistura não existe).
