# Roteiro: concorrência ao vivo (série "eu medi", Short 2), 2026-11-01

**Atualização após o pedido de render:** a versão pt-BR está pronta em
[`final.pt.mp4`](final.pt.mp4), com 41,7 s, voz e efeitos; o `medicao.json` está limpo
e a conferência de áudio passou. Detalhes em
[`rotina-2026-11-01.md`](rotina-2026-11-01.md#retomada-manual-render-em-português).
O bloco "O que falta" abaixo é o registro da parada original da rotina; en/ig
continuam sem render e a revisão humana do pt permanece pendente.

Pauta: `../serie-conceitos/pautas/02-concorrencia.md`, ângulo A, com a versão `atomic` (cabe em 45 s). Medição em
`demo/resultado.txt` (gcc 15.2.0 `-O2 -pthread`, Ryzen 7 5700U, 12 processadores visíveis, `cpu_probe` 0,059 s no
início da rotina, 2 threads × 1.000.000 somas, 15 rodadas por versão). O contador da versão sem proteção é
`volatile`, e o `objdump` no `resultado.txt` mostra o laço (`mov`, `add`, `mov`, sem `lock`). Narração em
`narracao.pt.json` (`@viniciusnakahara`) e `narracao.en.json` (`@baixo.nivel.dev.s` e o Reel do `koiti.dev`).
Todo número da fala e da tela deve ter entrada em `medicao.json` (ainda por escrever; ver "O que falta").

| Cena | Tela | Origem de cada número |
| --- | --- | --- |
| `gancho` (hook, capa) | "2 threads. 1 contador. O total deveria dar 2.000.000." | `2 threads x 1000000 somas` no cabeçalho; `esperado=2000000` em cada rodada |
| `codigo` | 1.000.000 somas por thread; Versão 1 sem proteção, 2 mutex, 3 atomic | cabeçalho; "Versão 1/2/3" são nomes |
| `resultado` (turn) | sem proteção (mediana) 1.130.174 contra mutex 2.000.000 | `## resumo versao=sem total mediana=1130174 minimo=999916 maximo=1325842`; mutex: `minimo=2000000 maximo=2000000` nas 15 rodadas. A fala diz "perto de um milhão" (999.916) e "mais de um milhão e trezentos mil" (1.325.842) |
| `tempo` | sem proteção 11,0 · atomic 21,4 · mutex 92,2 ms | `## resumo versao=... ms mediana=` das três; a fala arredonda para onze, vinte e um e noventa e dois |
| `fecho` (invite) | cartão final, "código na descrição" | nenhum número |

## Regras seguidas

- Só o que a medição mostra. A fala não diz por que o total encolhe (leitura e escrita não atômicas, cache,
  escalonador): o fecho pergunta ao público e o comentário fixado traz a medida inteira.
- Nenhuma razão na tela (mutex ÷ sem proteção não está no arquivo; ADR 020).
- Os números são desta máquina; o texto não generaliza. O tempo da versão sem proteção (11,0 ms) é de uma conta
  errada, e a tela o rotula "total errado".
- O `footer` traz o ambiente e fica fora do `vp medicao`.

## O que falta

1. **Etapa 5 parou:** `node` do ambiente da rotina (`/usr/bin/node` 22.22.1) não carrega o kit (`ERR_UNKNOWN_FILE_EXTENSION
   .ts` em `content.schema.ts`). O `video.mjs` precisa do Node do nvm (o da sessão interativa). Sem `validate` e
   `inspect`, os rótulos longos ("sem proteção (total errado)", "com mutex (as 15 rodadas)") e a grade de 4 células
   não foram conferidos.
2. `medicao.json` e `vp medicao` limpo nas pastas `-pt` e `-en`; `vp traducao short-concorrencia-en`;
   `traducao.json` em `-en`.
3. `review` do kit e os quadros; voz no Modal, `tempos`, render ×3, `sfx`, `juntar --sfx`, `conferir_audio.py`.
4. Glossário de pronúncia pt (`voice/glossary.json`): "threads", "mutex" e "atomic" saem do português; o dono ouve a
   voz antes de aprovar.
5. Pasta `concorrencia/` no `baixo-nivel-demos` público (`contador.c` e `medir.sh`) antes de agendar: a fala diz
   "código na descrição".
6. Títulos no vidIQ só com o pedido do dono. Provisórios: "Dois threads, um contador, e o total errado" /
   "Two threads, one counter, wrong total".
