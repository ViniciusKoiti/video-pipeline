# Roteiro: memory leak ao vivo (série "eu medi", Short 1), 2026-10-31

Pauta: `../serie-conceitos/pautas/01-memory-leak.md`, ângulo A. Medição em `demo/resultado.txt` (gcc 15.2.0 `-O2`,
Ryzen 7 5700U, `cpu_probe` 0,05 s, 15 rodadas de 10 s por versão, um bloco de 64 KB a cada 1 ms). Narração em
`narracao.pt.json` (`@viniciusnakahara`) e `narracao.en.json` (`@baixo.nivel.dev.s` e o Reel do `koiti.dev`).
Todo número da fala e da tela tem entrada em `medicao.json`; `vp medicao` confere.

| Cena | Tela | Origem de cada número |
| --- | --- | --- |
| `gancho` (hook, capa) | "Mesmo programa. Só esqueci o free." | "sete mil vezes em dez segundos": `iteracoes=7278` da rodada 1 sem free (as rodadas vão de 7.278 a mais; a fala arredonda para baixo), `t=10s` |
| `codigo` | 64 KB por bloco; as duas versões (com e sem `free`) | `bloco 64 KB` no cabeçalho; "Versão 1/2" são nomes |
| `resultado` (turn) | com free 2,1 MB contra sem free 491,0 MB, aos 10 s | `## resumo` das duas versões: medianas 2.1 e 491.0; "dois megabytes" e "quatrocentos e noventa" arredondam |
| `curva` | 5 pontos da rodada 1 sem free: 2 s 83,9 · 4 s 166,5 · 6 s 265,5 · 8 s 364,1 · 10 s 457,0 MB | linhas `t=Ns rss_mb=` da rodada 1; a fala diz os extremos, 42,7 MB em 1 s e 457,0 em 10 s |
| `fecho` (invite) | cartão final, "código na descrição" | nenhum número |

## Regras seguidas

- Só o que a medição mostra. A fala não diz para onde vai a memória nem por quê (páginas, alocador): o fecho
  pergunta ao público e o comentário fixado traz a medida inteira.
- A pauta dizia "mil vezes"; a medição deu 7.278 iterações na rodada 1 (e mais nas outras, porque o `nanosleep`
  de 1 ms dorme mais que 1 ms). A fala diz "sete mil", arredondado para baixo, com a rodada 1 como origem.
- Nada de razão na tela (`showRatio: false`): 491 ÷ 2,1 não está no arquivo (ADR 020).
- O `footer` traz o ambiente e fica fora do `vp medicao` (legenda conferida de olho).
- Os números da tela são da máquina do dono; o texto não generaliza.

## O que falta

1. Humanizer no pt: a narração abaixo já passou pelas regras da skill (sem "não é X, é Y", sem anúncio, frases
   de 8 a 18 palavras); conferir de novo depois da voz.
2. `vp medicao` limpo nas pastas `-pt` e `-en`; `vp traducao` e o gate `translation` do `-en` (dono).
3. `inspect` e `review` do kit; o dono olha os quadros.
4. Voz clonada (Modal) só com o pedido do dono; depois `tempos`, render ×3 (pt, en, en com a janela para o Reel,
   que depende da licença da pele), `sfx.json`, `juntar --sfx`, `conferir_audio.py`.
5. Pasta `memory-leak/` no `baixo-nivel-demos` público antes de agendar (a fala diz "código na descrição").
6. Títulos no vidIQ (5 créditos cada) só com o pedido do dono. Provisórios: "Mesmo programa, só esqueci o free" /
   "Same program, I just forgot the free".
