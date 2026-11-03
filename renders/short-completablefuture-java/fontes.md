# Fontes do Short CompletableFuture (Java)

Registro de 2026-11-02. Documento primário: Javadoc do `java.util.concurrent.CompletableFuture`, JDK 25
(`https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/CompletableFuture.html`).

**Atenção:** os trechos abaixo vieram de uma extração automática da página (WebFetch), não de uma leitura
direta. Conferir cada frase na página antes de publicar o roteiro. Não há segunda fonte primária fichada
ainda; o Javadoc do JDK 25 é a única fonte de mecanismo deste Short.

## Mecanismo, com a frase registrada

| Afirmação usada no roteiro | Trecho registrado (inglês, como na página) | Onde aparece |
| --- | --- | --- |
| `CompletableFuture` é um `Future` que pode ser completado explicitamente e aceita funções dependentes | "A Future that may be explicitly completed (setting its value and status), and may be used as a CompletionStage, supporting dependent functions and actions that trigger upon its completion." | `desenho`, `codigo` |
| `supplyAsync` roda a tarefa de forma assíncrona; sem executor explícito, usa o `ForkJoinPool.commonPool()` | "Returns a new CompletableFuture that is asynchronously completed by a task running in the ForkJoinPool.commonPool() with the value obtained by calling the given Supplier." | `codigo` (o Short passa o pool explicitamente) |
| `thenCombine` executa a função só quando as duas etapas terminam normalmente | "Returns a new CompletionStage that, when this and the other given stage both complete normally, is executed with the two results as arguments to the supplied function." | `desenho`, `codigo` |
| `orTimeout` completa excepcionalmente com `TimeoutException` se o prazo passar | "Exceptionally completes this CompletableFuture with a TimeoutException if not otherwise completed before the given timeout elapsed." | `prazo` |
| `join` lança `CompletionException` com a causa original | "...this method throws an (unchecked) CompletionException with the underlying exception as its cause." | `prazo` (não é lido em voz) |
| O parâmetro de `cancel` não interrompe a tarefa nesta implementação | "this value has no effect in this implementation because interrupts are not used to control processing." | `prazo` (apoio à frase sobre a tarefa) |

## O que a documentação não diz

- Se `orTimeout` interrompe ou cancela a tarefa que ainda roda. A página descreve só a conclusão do future
  com `TimeoutException`. Por isso o Short não diz "a tarefa para": diz o que a **demonstração** mediu, que a
  tarefa seguiu até o fim. A regra de quem está certo fica com a medição.

## Limites da fonte

- Uma fonte primária. Sem segunda fonte (artigo, JEP, documentação do pool) fichada; o roteiro não cita nenhuma.
- A página foi lida em duas partes (offset 0 e 100000); a seção de `orTimeout` veio na segunda.
