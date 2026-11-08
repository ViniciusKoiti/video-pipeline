# Fontes: circuit breaker em Java

Consultadas em 2026-11-05 por fetch das URLs abaixo. Excertos literais em `fontes/excertos.md`.
As fontes explicam o padrão; os parâmetros e resultados vêm exclusivamente da demo local.

| ID | Fonte primária | Uso |
| --- | --- | --- |
| F1 | Martin Fowler, Circuit Breaker, 2014-03-06. https://martinfowler.com/bliki/CircuitBreaker.html | Chamadas protegidas, limiar de falhas, erro sem invocação, teste meio-aberto, recursos retidos |
| F2 | Microsoft, Azure Architecture Center, Circuit Breaker pattern. https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker | Estados e custo de permanecer aberto após a recuperação |
| D1 | `demo/Demo.java`, `demo/BreakerTest.java`, `demo/medir.sh` e `demo/resultado.txt` | Implementação didática Java e execução local concluída; nenhum arquivo da demo foi alterado nesta preparação |

## Evidência local

`demo/resultado.txt`: execução concluída em 2026-11-05, OpenJDK 25.0.4.1, quinze rodadas por modo,
JVM nova sem aquecimento, ordem alternada, execução sequencial. Todas as sondas registradas ficaram abaixo
do limite de interrupção. Isso não garante ausência de ruído.

Simulação com `Thread.sleep`, fila ilimitada e pool de threads. Não mede rede, banco, biblioteca nem produção.
As contagens apresentadas são medianas dos valores por rodada, não soma das rodadas.
Recusa é erro, nunca pagamento concluído nem degradação tratada como sucesso.

Não usar a redução de latência como ganho: essa distribuição inclui fila, erros e recusas.
A redução de chamadas não é um percentual de sucesso nem prova que o serviço inteiro permaneceu disponível.
O breaker não cancela chamadas já em voo; cinco falhas não significam apenas cinco chamadas na dependência.
Os parâmetros escolhidos não são defaults de Java nem recomendações universais.

## Direitos e ativos

Trechos textuais curtos para rastrear as afirmações, com atribuição e URL; nenhuma imagem das fontes será usada.
Os diagramas são declarativos e originais, compostos com o motion-video local. Sem assets externos, Lottie,
pele do apresentador ou promessa de código público. Publicação e gates humanos permanecem pendentes.
