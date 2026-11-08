# Plano de novembro de 2026: Shorts técnicos (série "eu medi")

Proposta de 2026-11-03, a pedido do dono. **Aprovado pelo dono em 2026-11-03** (cadência de três por semana, segunda,
quarta e sábado 12h, e o calendário abaixo). Vale para os três canais da série: YouTube pt
(@viniciusnakahara), YouTube en (@baixo.nivel.dev.s) e Instagram koiti.dev (en). O Cena e Conceito (ensaios longos)
fica fora deste plano.

## O que já está no ar ou agendado

| Data (BRT) | Tema | Canais | Estado |
| --- | --- | --- | --- |
| Dom 01/11 | Concorrência em C | YT pt, YT en | publicado |
| Seg 02/11 18h | CompletableFuture | IG | publicado |
| Ter 03/11 10h | CompletableFuture | YT pt, YT en | agendado |
| Qua 04/11 12h | Índices no SQLite | YT pt, YT en, IG | agendado |
| Sáb 07/11 12h | Memory leak | YT pt, YT en, IG | agendado |

São 5 Shorts técnicos de 01 a 07/11. A dúvida cega já apontou isso como risco da política de conteúdo repetitivo
(CLAUDE.md §12; ADR 036, "Trade-offs").

## Cadência proposta a partir de 09/11

**Três por semana: segunda, quarta e sábado, 12h BRT**, nos três canais ao mesmo tempo. Motivos:

- Fica abaixo da semana de 01 a 07/11 e bem abaixo dos sete por semana que a ADR 036 marca como risco literal.
- Mantém o sábado 12h da série original e dá dois dias entre um Short e outro para ler as primeiras horas.
- A rotina diária continua produzindo um por dia quando há pauta aprovada: a produção fica à frente da publicação
  (estoque de uns 4 Shorts prontos), e o gate 4 e o agendamento continuam com o dono.

## Calendário de publicação

| Data (BRT, 12h) | Tema | Pauta | Produção (rotina, 06h) |
| --- | --- | --- | --- |
| Seg 09/11 | Virtual threads em Java | aprovada | 04/11 |
| Qua 11/11 | Circuit breaker em Java | aprovada | 05/11 |
| Sáb 14/11 | Rate limiter em Java | aprovada | 11/11 (movida de 06/11, 2026-11-05) |
| Seg 16/11 | Consistent hashing em Java | aprovada | 07/11 |
| Qua 18/11 | Idempotência em Java (o pagamento cobrado duas vezes por um retry) | **a escrever e aprovar** | 08/11 |
| Sáb 21/11 | HashMap e colisões em Java (`hashCode` ruim × bom) | **a escrever e aprovar** | 09/11 |
| Seg 23/11 | Cache em Java (taxa de acerto e *cache stampede*) | **a escrever e aprovar** | 10/11 |
| Qua 25/11 | Garbage collector em Java: como funciona (G1 × ZGC, pausas e p99 como consequência) | aprovada; reenquadrada em 2026-11-05 | 06/11 (antecipada de 11/11) |
| Sáb 28/11 | A definir depois da revisão de 14/11 (ver abaixo) | — | — |
| Seg 30/11 | A definir depois da revisão de 14/11 | — | — |

Os quatro temas novos vêm da validação no vidIQ (`docs/pesquisa/temas-serie-conceitos-vidiq-2026-11-03.md`):
idempotência (overall 62), HashMap (57), cache (55, +41%), garbage collector (54). As pautas precisam estar
aprovadas até **07/11** para a rotina produzir de 08 a 11/11. As duas vagas do fim do mês ficam abertas para o que
as métricas mostrarem; candidatos: Árvores (pauta antiga aprovada, em C, adiada), retry com backoff, bulkhead.

## Leituras de métricas (7 e 28 dias, `vp metricas`)

| Tema | Publicação | 7 dias | 28 dias |
| --- | --- | --- | --- |
| Concorrência em C | 01/11 | 08/11 | 29/11 |
| CompletableFuture | 03/11 | 10/11 | 01/12 |
| Índices no SQLite | 04/11 | 11/11 | 02/12 |
| Memory leak | 07/11 | 14/11 | 05/12 |
| Virtual threads | 09/11 | 16/11 | 07/12 |
| Circuit breaker | 11/11 | 18/11 | 09/12 |
| Rate limiter | 14/11 | 21/11 | 12/12 |
| Consistent hashing | 16/11 | 23/11 | 14/12 |
| Idempotência | 18/11 | 25/11 | 16/12 |
| HashMap | 21/11 | 28/11 | 19/12 |
| Cache | 23/11 | 30/11 | 21/12 |
| Garbage collector | 25/11 | 02/12 | 23/12 |

## Pontos de decisão

- **Até 07/11:** aprovar (ou trocar) as pautas de idempotência, HashMap, cache e garbage collector.
- **Sáb 14/11, revisão da série:** com as leituras de 7 dias dos quatro primeiros (concorrência, CompletableFuture,
  índices, memory leak): views, retenção nos 3 s iniciais, comentários sobre a própria aplicação (hipóteses das
  pautas). Decidir: manter três por semana ou mudar; o que muda no molde (duração, gancho, a versão en com 50 s);
  e os temas de 28 e 30/11.
- **Seg 30/11:** fechamento do mês com as leituras de 28 dias dos primeiros e a decisão de dezembro.

## Riscos

- **Conteúdo repetitivo:** a mesma abertura e o mesmo fecho são permitidos se o corpo varia (§12). Aqui varia a
  demonstração, a medição e a animação de cada tema. Manter três por semana e não repetir o mesmo desenho de cena
  em Shorts seguidos.
- **Rotina parada:** sem pauta aprovada, a rotina para (ADR 036). Com este plano, a fila tem pautas até 11/11.
- **Gate 4 acumulado:** quatro Shorts prontos de 04 a 07/11 pedem quatro revisões suas; o plano dá folga até a
  véspera de cada publicação.
- **Medição na máquina:** dias com o Windows pesado adiam a produção (a sonda para a rotina); o estoque absorve.
