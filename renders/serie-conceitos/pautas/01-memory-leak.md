# Pauta 1: memory leak, sábado 2026-11-07, 12h

Série "eu medi" (`../serie.md`). Nada foi medido, gravado nem renderizado; a medição roda depois do ok do lote.

## Por que este conceito abre a série

Memory leak é o conceito mais **visível** dos quatro: um número que só sobe, na tela, enquanto o programa roda.
Todo iniciante já ouviu o termo e quase ninguém viu a memória subir ao vivo. A demonstração não precisa de
explicação para ser entendida: duas versões do mesmo programa, uma barra sobe e a outra fica parada.

## Os ângulos

### A. A memória que só sobe (recomendado)
- **Gancho (3 s):** "Esse programa faz a mesma coisa mil vezes. Olha a memória."
- **Demonstração:** um programa em C num laço que aloca um bloco a cada iteração e não libera (`malloc` sem
  `free`); a versão B libera. A cada segundo o próprio programa lê o RSS em `/proc/self/statm` e imprime
  `t=Ns rss=X MB`. Rodar os dois por 10 s, 15 repetições para o valor final, mediana.
- **O que a medição precisa responder:** quanto o RSS da versão A sobe em 10 s (MB e MB por segundo), se a
  versão B fica estável, e se o número é o mesmo entre rodadas (mediana e extremos).
- **Risco:** se o alocador reaproveitar páginas e o RSS subir pouco, o efeito fica fraco. Mitigação: blocos de
  tamanho que force página nova (ex.: 64 KB) e escrita no bloco (`memset`), senão a página nem é mapeada.
- **Por que eu escolheria:** é o único ângulo em que a tela mostra o conceito sem uma palavra de explicação.

### B. O vazamento que o `valgrind` denuncia
- **Gancho:** "Rodei meu programa dentro de outro programa. Ele me contou tudo que eu esqueci."
- **Demonstração:** o mesmo programa A no `valgrind --leak-check=full`; na tela, o resumo "definitely lost: N
  bytes in M blocks". Medido: bytes e blocos, igual entre rodadas.
- **Risco:** o resumo do valgrind é texto denso; em vertical, precisa de recorte e fica menos visual. Depende de
  `valgrind` instalado (apt, sem custo).

### C. Até a máquina reclamar
- **Gancho:** "Deixei o programa vazar até o sistema matar ele."
- **Demonstração:** o programa A até o OOM killer; tempo até morrer e o RSS final.
- **Risco:** na máquina limitada do dono (CLAUDE.md §3) derrubar a RAM do WSL pode travar o resto; medida
  pouco repetível. Fica fora da v1.

## Demonstração planejada (ângulo A)

- `demo/vazamento.c`: `--libera` liga o `free`. Imprime `t`, `rss_mb` a cada segundo por 10 s, mais a linha
  de ambiente (gcc, flags, CPU, data) no começo, como o `resultado.txt` da lista ligada.
- `demo/resultado.txt`: as duas versões, 15 repetições, mediana do RSS aos 10 s e os extremos.
- Tela: cena `codigo` com as poucas linhas do laço (uma versão com `free`, a outra sem), cena `resultado` com a
  comparação (`comparison`, `mode: side`: MB aos 10 s, A contra B), cena `curva` com os pontos a cada segundo
  (`categories` ou `chart`, se o kit renderizar bem 10 pontos em vertical; decidir no `review`).
- Legenda do ambiente no `footer`.

## Forma (35 a 45 s)

1. Gancho, 3 s: a frase do ângulo, a barra começando a subir.
2. Código, 10 s: o laço, as duas versões lado a lado.
3. Resultado, 12 s: os MB aos 10 s das duas versões; a curva.
4. Só o que a medição mostra, 8 s: "a versão sem `free` sobe X MB por segundo; a outra fica em Y".
5. Fecho, 6 s: "Quer saber para onde vai essa memória? Comenta aqui, que o código está na descrição."

## Hipótese (copiar para `metrics.json`)

Um Short com a memória subindo ao vivo, medida na máquina do dono, retém mais que uma explicação genérica de
memory leak. Variável: o número medido no gancho. Medida: retenção e views aos 7 e 28 dias contra o
`short-lista-ligada`.

## O que o dono decide

1. Ângulo A, B ou C (recomendo A; B pode ser o segundo Short sobre o tema, mais adiante).
2. O tamanho do bloco e a duração (10 s) ficam comigo, registrados no `resultado.txt`.
3. Título provisório: "Mesmo programa, só esqueci o free" (pt) / "Same program, I just forgot to free" (en);
   pontuação no vidIQ só com o pedido dele.

## O que esta pauta não diz

Nenhum número: não há medição. Nada sobre o porquê (páginas, alocador, fragmentação) entra na fala sem fonte
registrada; vai para a pergunta do fecho e para o comentário fixado, com a medida.
