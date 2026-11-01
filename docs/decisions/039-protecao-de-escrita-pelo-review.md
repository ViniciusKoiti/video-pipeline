# ADR 039 — Proteção de escrita derivada do review.json

Data: 2026-11-01. Status: aceita (RF1 do [fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md),
gap G01 da [análise](../analise-gaps-solid-2026-10-31.md)).

## Contexto

`vp approve` grava só no `review.json`. A proteção do §2.6 vinha de duas outras fontes: o `review_status` de
topo do JSON (só os ativos o têm) e as `protected_outputs` do `manifest.json` (só `approve_step`, que nenhum
comando usa). Resultado: fontes, fichas, roteiro e saídas do gate 4 aprovados pelo CLI podiam ser
sobrescritos pelo código, e `vp reopen` era placeholder.

## Decisão

- **Uma autoridade:** o `review.json`. `app/pipeline/protection.py` (`ReviewWriteGuard`, porta `WriteGuard`)
  recalcula a proteção a cada consulta; nada é projetado no `manifest.json`.
- **O que protege:** o que cada gate carimba, enquanto a última decisão dele é "aprovado" e o hash revisto
  ainda bate com o conteúdo (hash normalizado ou o legado, de arquivo inteiro). Gate 1: `sources.json` e
  `facts.json`; gate 2: `scenes.json` e `outline.md`; gate 3: `assets/<id>.json` e a mídia; gate 4: o render
  mais acabado e os textos que existiam quando foi carimbado (um `final.mp4` novo não é sobrescrita: o gate
  muda e a versão é revista, #120). Conteúdo mudado por fora derruba a aprovação e, com ela, a proteção.
- **Escrita que não muda o carimbo passa:** com o conteúdo candidato em mãos, o guard confere o hash
  normalizado depois da escrita. Trocar `asset_id` (gate 3) e regenerar o bloco de números (`vp numeros`)
  seguem permitidos; decisão legada, sem a normalização, não ganha essas exceções. Sem candidato (troca de
  binário), qualquer alteração de arquivo carimbado é recusada.
- **Reabertura:** `app/pipeline/reopen.py` e `vp reopen --step S [--asset A] --reason ...` acrescentam uma
  decisão `changes_requested` com autor e motivo (`reaberta: ...`) e não editam as anteriores. Libera só o
  alvo pedido. Reabrir um ativo devolve o `review_status` do JSON dele a `needs_review`, o que a aprovação
  tinha refletido; é a única escrita de código em arquivo aprovado, e é a própria reabertura.
- **`ReviewLog.latest` segue a posição no log**, não o `at`: o log só acrescenta, o CLI grava sem
  microssegundos e o relógio do WSL pode recuar; pelo `at`, uma reabertura no mesmo segundo ou com relógio
  atrasado perderia para a aprovação.
- `write_output` passou a exigir um `guard`; não toma o lock do episódio (quem chama o segura), para não
  aninhar com o lock de `run_step` (RF2).

## Fora do escopo

Integrar o guard aos escritores concretos (fontes, ativos, pacote do Short) é RF5/RF6. O gate de tradução
(ADR 034, proposta) ainda não tem alvos protegidos.
