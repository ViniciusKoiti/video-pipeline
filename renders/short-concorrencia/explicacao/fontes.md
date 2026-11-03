# Explicação do contador: fontes e limites

Pedido do dono em 2026-11-01: explicar a perda dos incrementos e o papel do atomic.
Esta revisão altera a escolha original de deixar o porquê como pergunta ao público.
A medição e o código originais continuam em `../demo/`, sem nova execução.

## Fontes baixadas

- **C11**: [WG14, N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf),
  cópia `fontes/n1570.pdf` e texto extraído `fontes/n1570.txt`.
  §7.17.7.5: “These operations are atomic read-modify-write operations”.
  §5.1.2.4 p25: “Any such data race results in undefined behavior.”
- **MUTEX**: [Oracle, pthread_mutex_lock Syntax](https://docs.oracle.com/cd/E19120-01/open.solaris/816-5137/sync-117/index.html),
  cópia `fontes/pthread-mutex-lock.html`.
  Trecho: “the calling thread blocks until the mutex becomes available.”
- **DEMO**: `../demo/contador.c`, função `soma`: leitura/soma/escrita no contador
  `volatile`, trecho com `pthread_mutex_lock`/`pthread_mutex_unlock` e
  `atomic_fetch_add(&com_atomic, 1)`.
- **MEDIDA**: `../demo/resultado.txt`: mesmas 15 rodadas e medianas da versão anterior.

## Fichas usadas na revisão

| ID | Afirmação ou imagem | source_ids | Limite |
| --- | --- | --- | --- |
| F01 | Incremento sem proteção pode perder atualização; exemplo dos dois threads lendo 10 e gravando 11 | DEMO, C11 | Ilustração didática do conflito; não é trace da execução. Em C, a corrida de dados tem comportamento indefinido. |
| F02 | Mutex permite um thread por vez no trecho protegido pelo mesmo mutex | MUTEX, DEMO | Todos os acessos ao contador nessa variante estão dentro do mesmo par lock/unlock. |
| F03 | `atomic_fetch_add` efetua a soma como uma operação indivisível de leitura/modificação/escrita | C11, DEMO | A garantia se refere à operação, não a qualquer expressão feita com um tipo atômico. |
| F04 | O exemplo atômico vai de 10 a 11 e depois a 12 | C11 | Aritmética didática: 10 + 1 + 1 = 12; não é nova medição. |
| F05 | Sem proteção 11,0 ms; atomic 21,4 ms; mutex 92,2 ms; ambos protegidos atingiram 2.000.000 | MEDIDA | Valores desta máquina e programa; não estabelece uma regra geral de desempenho. |

O texto foi revisto pelo método humanizer: linguagem falada, sem acrescentar causa
relativa a cache, escalonador ou instrução da CPU. Não afirma que atomic seja sempre
lock-free, que proteja um bloco inteiro ou que seja sempre mais rápido.

## Rastreio por cena

`gancho` e `resultado`: F05. `codigo`: F01. `mutex`: F02.
`atomic`: F03–F04. `tempo`: F05. `fecho`: F02–F03.

A versão anterior permanece em `../final.pt.mp4`. Esta revisão usa o episódio
`short-concorrencia-explicacao-pt` e não concede aprovações humanas.
