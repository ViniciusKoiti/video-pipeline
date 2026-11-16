# Rate limiter em Java: texto fechado antes da voz

Produção de 2026-11-16 (rotina `/short-diario`). Pauta aprovada em 2026-11-03:
`data/episodes/short-rate-limiter-java-pt/pauta.md`. Medição: `demo/resultado.txt` (2026-11-11, não refeita).
Fontes: `fontes.md`. Idioma original pt-BR; inglês deriva dele. Objetivo: **explicar**. Funil `topo`.

## Lição em uma frase

O token bucket gasta uma ficha por requisição e recusa quando elas acabam, então a rajada de um cliente passa só até
o tamanho do balde e os outros clientes deixam de esperar atrás dela; o custo é que qualquer pico maior que o balde,
legítimo ou não, também leva a recusa.

Aplicação: API Java com um robô em rajada e cinco clientes normais; o serviço de trás tem 10 vagas (simulado).
Decisão de System Design: pôr um limitador por cliente na entrada e escolher a taxa de enchimento e o tamanho do balde.
Benefício medido: mediana dos clientes normais de 2867 ms para 51 ms. Limite: 900 recusas ao robô; a recusa de um
pico legítimo é consequência do mecanismo, **não medida**. Título provisório: "Rate limiter em Java: o que acontece
com a 101ª requisição?" / "Rate limiter in Java (system design): what happens to request 101?".

## Narração pt-BR (6 cenas, 1 hook, 1 invite, 4 neutral; sem turn)

1. situacao (hook): O que acontece com a requisição 101 quando um robô dispara mil de uma vez?
2. balde: O token bucket ganha vinte fichas por segundo, até cem, e cada requisição gasta uma.
3. recusa: Sem ficha vem o erro quatrocentos e vinte e nove, sem chamar o serviço, então a rajada passa só até o tamanho do balde.
4. medido: Na simulação, os clientes normais foram de quase três segundos para 51 milissegundos.
5. limite: O robô levou novecentos erros, e um pico legítimo maior que o balde levaria o mesmo: taxa e tamanho do balde são a decisão.
6. fecho (invite): Qual tamanho de balde você escolheria para a sua API?

## Narration en

1. A bot fires a thousand requests at once: what happens to number 101?
2. The token bucket gains twenty tokens per second, up to a hundred, and each request spends one.
3. With no token left comes error four hundred and twenty-nine, without calling the service, so the burst passes only up to the bucket size.
4. In this simulation, normal clients went from almost three seconds to 51 milliseconds.
5. The bot took nine hundred rejections, and a legitimate spike bigger than the bucket would get the same: rate and bucket size are the decision.
6. What bucket size would you pick for your API?

## Rastreio

- Balde com taxa fixa, teto, gasto por unidade e recusa sem fichas: F2 (§3). "Cem" e "vinte por segundo": D1
  (`limite=` em `resultado.txt`), parâmetros da demo, não da RFC.
- 429 = "rate limiting": F1 (§4). A RFC não diz como se conta: a contagem por cliente é decisão da demo.
- "A de número cento e um" recusada, e a rajada de 1000 passa 100: D1 (`LimitadorTest`, `robo_aceitas=100`).
- "Sem chamar o serviço": D1 (`429 sem chamar o servico de tras`; `servico_atendidas` 1300 → 400).
- 2,9 s (2867 ms) → 51 ms: D1, `normais_mediana_ms`, medianas das 15 rodadas (extremos 2863–2870 e 51–51). A fala diz
  "quase três segundos" (arredondamento falado, tolerância 0,15 no `medicao.json`) e a tela mostra 2,9 s.
- 900 recusas: D1, `robo_recusadas` (900–900). 100 aceitas, 0 normais recusados.
- "Pico legítimo maior que o balde levaria o mesmo": **consequência do mecanismo** (F2: sem fichas suficientes não há
  passagem); não é número nem resultado medido. A fala diz "levaria", no condicional.
- Cenário simulado (Thread.sleep, threads virtuais, 10 vagas, 50 ms): dito no rodapé; nada de rede, banco ou produção.
  Sem alegar throughput, disponibilidade nem p99 na tela.

## Humanizer revisado antes da voz

Revisão feita antes da primeira `vp short voz`, com a skill `humanizer-narracao`: fatos, números e fontes preservados;
orações ligadas por "e/mas/então"; sem anúncio antes do ponto, sem contraste "não é X, é Y", sem trio forçado nem
fecho de efeito; sem "eu não encontrei". Números na fala: por extenso quando o detector do `vp medicao` os lê (mil, vinte, cem, quatrocentos e vinte e nove,
novecentos); em dígitos, com troca no glossário só para a voz, quando ele não lê ("101" → "cento e um", "51" → "cinquenta e
um"; mesmos termos em inglês). A tela traz 101, 429, 2,9 s, 51 ms, 900.
Glossário por idioma: `token bucket`, `API`, `101` e `51` (pt); `API`, `101` e `51` (en). Sem "Java" na fala (aparece no rodapé).

Estimativa (contagem por espaços, depois de encurtar o texto antes da primeira voz): pt 104 palavras ≈ 47 s a 2,2
palavras/s; en 105 ≈ 48 s. Acima dos 35 a 45 s da pauta; mantido porque cada cena carrega a lição ou o número medido, e
o fecho `invite` precisa de ~4 s para passar no nivelamento (ADR 054). Os tempos finais vêm dos WAVs.
