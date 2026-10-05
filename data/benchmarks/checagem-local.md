# Checagem local: prompt `prompts/local/checagem.md` em modelo pequeno (#27)

Medição do prompt de uma afirmação contra um trecho, com o Ollama local, no episódio aprovado
`votorantim-dinheiro`. Comando: `scripts/provisorio/checagem_local.py votorantim-dinheiro --modelo <m>`
(semente 1, 12 afirmações reais e 8 casos de cada mutação). Relatório completo fica em `data/cache/` (fora do Git).

**Gabarito:** as afirmações reais valem `SUSTENTA` (passaram pelo verificador e pelos gates, o que é
suposição); as mutações são mecânicas: número trocado (`DIVERGE`), trecho de outra fonte (`SEM_SUPORTE`),
superlativo acrescentado ao fim ("Foi o maior de todo o país.", `EXAGERO`).

## `qwen3:4b` · 2026-10-05 · sonda de CPU 0,06 s · temperatura 0

| Métrica | Resultado |
|---|---|
| JSON válido | 36 de 36 |
| Alarme falso (real ≠ `SUSTENTA`) | 0 de 12 |
| Erro pego (mutação ≠ `SUSTENTA`) | 22 de 24 (92%) |
| Erro que passou como `SUSTENTA` | 2 de 24, os dois superlativos |
| Rótulo certo: número trocado | 7 de 8 (o outro saiu `EXAGERO`) |
| Rótulo certo: trecho de outra fonte | 8 de 8 |
| Rótulo certo: superlativo | 3 de 8 (`EXAGERO` 3, `SEM_SUPORTE` 3, `SUSTENTA` 2) |
| Tempo por chamada | mediana 31 s, máximo 179 s (carga do modelo); 23,7 min no total |

## Leitura

- Como alerta, serve: não acusou nenhuma afirmação real e pegou 92% das alteradas. Como rótulo, o
  superlativo é o ponto fraco, e os dois que passaram vêm de afirmações da mesma cena (S10, trecho E8).
- A mutação de superlativo vem numa frase separada ao fim. Um superlativo dentro da frase, como nos roteiros
  reais, pode ser mais fácil ou mais difícil; o gabarito não mede isso.
- 31 s por chamada torna a checagem de um episódio inteiro (centenas de afirmações) uma tarefa de horas na
  CPU. Serve como segunda leitura de uma amostra, não como substituto do `vp check` nem do verificador.
- O `id` dos casos repete quando duas afirmações da mesma cena citam o mesmo trecho; a medição não é afetada.

## Pendente

- `qwen3.5:9b` (padrão do `providers.toml`): mesma rodada, só com a máquina livre.
- Ajuste do prompt (superlativo) e nova rodada com outra semente, para não ajustar sobre os mesmos 36 casos.
