# Roteiro: CompletableFuture em Java (série "eu medi", Short da fila Java)

Pauta: `data/episodes/short-completablefuture-java-pt/pauta.md`, recorte aprovado pelo dono em 2026-11-02.
Pendente do dono: estágio do funil (`topo`, `meio` ou `fundo`) e chamada final. Duração-alvo: 35 a 45 s
(padrão da série; o dono não mudou).

Pergunta central: como compor duas chamadas independentes com `CompletableFuture`, e que cuidados de execução
e falha isso exige. Promessa: acompanhar uma requisição até a resposta e ver onde o future, a composição e o
prazo entram na decisão de arquitetura.

## Origem de cada número

Medição própria: `demo/resultado.txt` (Demo.java, `medir.sh`, OpenJDK 25.0.4.1, 15 rodadas por modo). As
latências das consultas são **simuladas** (300 ms e 200 ms, constantes do código): a medição mostra o efeito
da composição sobre o tempo de uma requisição com essas dependências, não o tempo de um banco ou de uma API
real. A fala diz isso no gancho da demonstração (`comparacao`).

| Cena | Tela | Origem |
| --- | --- | --- |
| `desenho` | pool de 4 threads | `pool fixo de 4 threads` no cabeçalho (constante) |
| `comparacao` | sequencial 501 ms; composto 309,5 ms | medianas `modo=sequencial` (501.0) e `modo=composto` (309.5) |
| `prazo` | prazo de 500 ms; resposta com timeout | `orTimeout 500 ms` no cabeçalho (constante) |
| `prazo-medido` | resposta 508,1 ms; tarefa termina 2006,1 ms | medianas `modo=timeout` (508.1) e `tarefa_terminou_em_ms` (2006.1) |

## Fontes do mecanismo

`fontes.md` (Javadoc do JDK 25, frases registradas e conferência pendente na página). O roteiro não
afirma o que o Javadoc não diz: sobre `orTimeout` e a tarefa subjacente, a fala diz o que a demonstração
mediu, e nada além disso.

## Regras seguidas

- Nenhum tempo ou ganho percentual sem medição; a fala não generaliza para outras aplicações.
- Java explícito: `CompletableFuture`, `supplyAsync`, `thenCombine`, `orTimeout`.
- A decisão de System Design aparece na cena `desenho` (requisição, pool, duas consultas, combinação) e
  na `prazo`, com o benefício (latência do maior caminho, no exemplo) e o limite (prazo que não para a
  tarefa; pool com capacidade fixa).
- Fecho em pergunta sobre a própria API do espectador; sem convite a outra linguagem nesta versão.

## Fora deste Short

- Virtual threads, programação reativa e comparação com outras linguagens (pauta, recorte).
- Qualquer afirmação de que `CompletableFuture` "elimina bloqueios" ou "aumenta a capacidade".

## A lição em uma frase (versão de 2026-11-02, aprovada pelo dono)

1. **Composição:** a latência do caminho composto é a da consulta mais lenta, não a soma (medido: 309,5 contra 501 ms).
2. **CompletableFuture:** uma caixa que ainda não tem o resultado; o `thenCombine` espera as duas encherem.
3. **Prazo:** o timeout responde a quem chamou, mas a tarefa segue e a thread do pool fica presa até o fim
   (medido: resposta aos 508,1 ms, tarefa aos 2006,1 ms). Apoio da frase "thread presa": a tarefa é um
   `Thread.sleep` rodando no `newFixedThreadPool(4)` do `Demo.java`; enquanto ela roda, ocupa uma thread do pool.
   É estrutura da demonstração, não número medido.

Cada cena de explicação diz uma dessas regras na fala; a tela repete, não substitui.
