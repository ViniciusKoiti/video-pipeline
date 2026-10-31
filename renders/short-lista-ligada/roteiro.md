# Roteiro: lista ligada, ordem dos nós na memória (ângulo B), 2026-10-30

Narração em `narracao.pt.json` (`@viniciusnakahara`) e `narracao.en.json` (`@baixo.nivel.dev.s`). Cena por linha;
os `id` abaixo são os do futuro JSON do motion-video (ainda não escrito). ~38 s de fala a 2,5 palavras/s.

| Cena | Tela | Origem de cada número |
| --- | --- | --- |
| `gancho` (hook, capa) | "Mesma lista. Mesmo código. Só a ordem na memória." | nenhum número |
| `codigo` | as linhas de `demo/lista.c` que montam e percorrem as duas listas | N = 10.000.000, `resultado.txt` |
| `resultado` (turn) | 27 a 30 ms contra ~2,4 s; razão 81,5× a 90,1× | `resultado.txt`, n=10000000, 2 rodadas (26,9 e 29,9 ms; 2420,8 e 2434,3 ms) |
| `tamanho` | tabela de N: 1 mil (1,0×) e 100 mil (10,6× a 13,6×) | `resultado.txt`, n=1000 e n=100000 |
| `fecho` (invite) | cartão final, link do repositório | [LINK] até a pasta estar no `baixo-nivel-demos` público |

## Regras seguidas

- Só o que a medição mostra. **A fala não explica o porquê** (cache, pré-busca): isso só entra com fonte
  confirmada, e o fecho promete a explicação como pergunta ao público, não como fato.
- Legenda da tela: "gcc 15.2, -O2, Ryzen 7 5700U, mediana de 15 repetições, 2026-10-30".
- "Dez vezes ou mais" em 100 mil nós, porque a razão variou entre as rodadas (10,6× a 38,7× em três execuções, uma
  delas só no terminal e fora do `resultado.txt`). Não dizer um número exato nessa linha.
- Os números do `resultado` e do `tamanho` são da máquina do dono; a tela diz isso, o texto não generaliza para
  "lista ligada é lenta".

## O que falta antes da voz

1. ~~Chamada final~~ **decidido (2026-10-30): "Comenta aqui"**. Há também um primeiro comentário fixado, a postar à
   mão no Studio depois de publicar (o Postiz não cobre): `posts/comentario-fixado.pt.txt` e `.en.txt`, com o
   `[LINK]` ainda em aberto.
2. A pasta `lista-ligada/` precisa estar no `baixo-nivel-demos` público antes de a fala dizer "código na descrição";
   senão a linha sai e fica o `[LINK]` no rascunho.
3. ~~Voz em inglês~~ **decidido (2026-10-30): a voz clonada do dono, nos dois idiomas** (Modal, ADR 024; gerar só
   com o pedido dele na sessão, e a pele do dono segue em `needs_review` se houver janela).
4. `humanizer-narracao` no pt: **ainda não rodei**. O `vp check` não se aplica a este formato; a conferência é
   número a número contra `resultado.txt`.
5. Gate de tradução do `-en`: **aprovado em 2026-10-30** pelo dono.
6. Dúvida cega e gate 4 antes de agendar, pela cadeia do ADR 025.
