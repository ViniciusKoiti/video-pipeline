# Rascunho dos posts: CompletableFuture em Java (não publicado)

## YouTube pt-BR (@viniciusnakahara)
Título (vidIQ 83): CompletableFuture: duas chamadas, uma resposta — e o custo disso

Descrição:
Em Java, uma API consulta preço e estoque. Com CompletableFuture, as duas consultas partem juntas e o
thenCombine espera as duas. Nesta medição, a resposta composta levou a da consulta mais lenta, não a soma.

Medido nesta máquina: OpenJDK 25.0.4, Ryzen 7 5700U, 15 rodadas por modo. As latências de preço (300 ms)
e estoque (200 ms) são simuladas no código da demonstração. Medianas: sequencial 501 ms; composto 309,5 ms;
resposta com prazo de 500 ms em 508,1 ms, com a tarefa terminando só aos 2006,1 ms.

Fonte do mecanismo: Javadoc do CompletableFuture (JDK 25).
Código da demonstração: [LINK, ainda não publicado]

A voz é a minha, clonada com IA. As animações foram criadas para este vídeo.

#Shorts #Java #CompletableFuture

## YouTube en (@baixo.nivel.dev.s)
Title (vidIQ 86): CompletableFuture in Java: two calls, one answer, and what it costs

Description:
In Java, an API checks price and stock. With CompletableFuture, both calls start together and thenCombine
waits for them. In this measurement, the composed response took as long as the slower call, not the sum.

Measured on this machine: OpenJDK 25.0.4, Ryzen 7 5700U, 15 runs per mode. The price (300 ms) and stock
(200 ms) latencies are simulated in the demo code. Medians: sequential 501 ms; composed 309.5 ms; response
with a 500 ms deadline at 508.1 ms, with the task only finishing at 2006.1 ms.

Mechanism source: CompletableFuture Javadoc (JDK 25).
Demo code: [LINK, not published yet]

The voice is mine, cloned with AI. The animations were made for this video.

#Shorts #Java #CompletableFuture

## Pendências antes de agendar
- Data e hora (série: sábado 12h BRT, se for a regra).
- Link do código: só com o repositório público; até lá, fica [LINK].
- Gate 4: assinatura do vídeo (VP_REVIEWER = Vinicius Koiti) depois de você ler os textos acima.
- Duração: pt 48,6 s, en 48,5 s; acima dos 45 s da série.
