# Excertos literais

Consulta: 2026-11-05. Os trechos abaixo foram conferidos contra o conteúdo retornado das URLs, não contra resumos.

## F1: Martin Fowler

https://martinfowler.com/bliki/CircuitBreaker.html

### F1a: bloquear sem invocar

> Once the failures reach a certain threshold, the circuit breaker trips, and all further calls to the circuit breaker return with an error, without the protected call being made at all.

### F1b: teste real

> There is now a third state present - half open - meaning the circuit is ready to make a real call as trial to see if the problem is fixed.

### F1c: resultado do teste

> Asked to call in the half-open state results in a trial call, which will either reset the breaker if successful or restart the timeout if not.

### F1d: recursos

> On their own, circuit breakers help reduce resources tied up in operations which are likely to fail.

> You avoid waiting on timeouts for the client, and a broken circuit avoids putting load on a struggling server.

## F2: Microsoft Azure Architecture Center

https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker

### F2a: espera e recursos

> These blocked requests might hold critical system resources, such as memory, threads, and database connections.

### F2b: fechado

> The request from the application is routed to the operation.

### F2c: custo após recuperação

> For example, if the circuit breaker remains in the Open state for a long period, it can raise exceptions even if the reason for the failure is resolved.

## D1: resultado local

Origem literal: `../demo/resultado.txt`, relativo a esta pasta.

```text
breaker=5 falhas consecutivas na ordem de conclusao; aberto=2000 ms; uma sonda meio-aberto
Simulacao local com Thread.sleep e fila ilimitada; nao e benchmark de producao, rede, banco ou biblioteca.
Recusas sao erros rapidos, nao pagamentos bem-sucedidos; erros inclui recusas.
recusadas_pos_falha: chegada programada >=3000 ms, mesmo com dependencia saudavel.
15 rodadas por modo, JVM nova sem aquecimento; ordem alternada por par, execucao sequencial.
RESUMO modo=sem-breaker metrica=chamadas_na_falha n=15 mediana=60 min=60 max=60
RESUMO modo=com-breaker metrica=chamadas_na_falha n=15 mediana=24 min=24 max=24
RESUMO modo=com-breaker metrica=recusadas n=15 mediana=133 min=132 max=133
RESUMO modo=com-breaker metrica=recusadas_pos_falha n=15 mediana=7 min=6 max=7
medicoes=30 status=COMPLETO
```
