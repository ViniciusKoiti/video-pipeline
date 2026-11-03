# Temas para a série "eu medi": brainstorm e validação no vidIQ (2026-11-03)

Pedido do dono: brainstorm de temas depois de virtual threads e circuit breaker, validado no vidIQ. Consultas de
2026-11-03 (`vidiq_keyword_research`, modo `research`, idioma en; `country_search` para BR; um `vidiq_outliers` de
Shorts), ~100 créditos. Os números são estimativas do vidIQ: `overall` (0–100, maior é melhor) combina volume e
concorrência; "buscas/mês" é a estimativa global; `<750` é o piso do vidIQ (pouca busca, ou a formulação não é a
que o público usa). Shorts são descobertos mais pelo feed que pela busca: a busca mede interesse, não garante views.

## Ranking (inglês, global)

| Tema | Termo medido | Overall | Buscas/mês | Concorrência | Tendência | Medível em Java só com o JDK? |
| --- | --- | --- | --- | --- | --- | --- |
| **Rate limiter** (token bucket) | rate limiter system design | **68** | 13.817 | **22** | +40% | Sim: aceitas × recusadas, latência protegida |
| Projeto de banco | database design | 66 | 31.424 | 37 | −6% | Amplo; o Short de índices já cobre um pedaço |
| Notificações | notification system design | 64 | 9.787 | 29 | +110% | Parcial: fila e fan-out simulados |
| **Consistent hashing** | consistent hashing | 63 | 27.352 | 42 | +29% | Sim: chaves que mudam de nó, módulo × anel |
| **Circuit breaker** (aprovado) | circuit breaker microservices | 63 | 3.676 | **23** | — | Sim (pauta aprovada) |
| **Idempotência** | idempotency | 62 | 9.249 | 35 | −24% | Sim: pagamento repetido por retry, com e sem chave |
| API design | api design | 60 | 9.425 | 39 | −2% | Amplo demais para um Short |
| **Virtual threads** (aprovado) | virtual threads java | 57 | 4.777 | 39 | — | Sim (pauta aprovada) |
| HashMap e colisões | hashmap java | 57 | 4.454 | 38 | — | Sim: `hashCode` ruim × bom |
| Cache | caching | 55 | 12.418 | 55 | +41% | Sim: acerto de cache e stampede |
| Rate limiting (variação) | rate limiting | 55 | 4.596 | 45 | — | — |
| Garbage collector | garbage collector java | 54 | 4.958 | 47 | — | Sim, mas mais pesado (G1 × ZGC, p99) |
| Load balancer | load balancer | 53 | 15.237 | 62 | −17% | Simulação; concorrência alta |
| Bloom filter | bloom filter | 50 | 5.030 | 57 | −71% | Sim, mas a busca está caindo |

Abaixo do piso (`<750` buscas/mês) com estas formulações: *circuit breaker pattern*, *rate limiter*, *retry
exponential backoff*, *java garbage collection*, *connection pooling*, *load balancing algorithms*, *n+1 query
problem*, *java parallel streams*, *caching system design*. A mesma ideia com outra formulação pode medir bem (ex.:
"circuit breaker pattern" < 750 × "circuit breaker microservices" 3.676): o título deve usar a formulação medida.

Referência: "system design" tem 415 mil buscas/mês (+15%), 60% da Índia; "system design concepts" +440%,
"system design tutorial" +242%, "system design for beginners" +39%. "Backend engineering" 15.871 (+78%).

## Brasil

`country_search` BR: "system design" ~14 mil buscas/mês no Brasil, "java" ~26,5 mil, "sql" ~32 mil, "spring boot"
~6,2 mil, "kafka" ~5,6 mil, "engenharia de software" ~50 mil. Os temas acima não foram medidos um a um em português
(o vidIQ devolveu poucos termos em pt para essa área); o canal pt usa o termo em inglês, como já faz com
CompletableFuture.

## Formato que funciona (outliers de Shorts)

Na busca "system design explained" (Shorts), o canal de referência que aparece com consistência é o Arjay McCandless
(135 mil inscritos): "System Design Patterns you need" (199 mil views, 2,2× a média do canal) e "System Design:
Typing Bubble" (133 mil, 1,6×): uma funcionalidade conhecida de app explicada pelo desenho do sistema. Os demais
resultados eram de outros nichos.

## Recomendação

1. **Rate limiter** (token bucket em Java): o melhor `overall` (68) com a menor concorrência (22) e busca crescendo;
   continua a minissérie de resiliência depois do circuit breaker. Título com "rate limiter" + "system design".
2. **Consistent hashing**: busca alta (27 mil) e crescente; demo visual forte (adicionar um nó move quase todas as
   chaves no módulo e poucas no anel).
3. **Idempotência**: liga com retry (o pagamento cobrado duas vezes); busca boa, embora caindo.
4. **HashMap e colisões**: Java puro, busca média, demo simples.

Retry com backoff e bulkhead medem pouco sozinhos: entram melhor como cena dentro de rate limiter/idempotência do que
como Short próprio. Nenhum destes temas está aprovado: cada um precisa de pauta e da decisão do dono.
