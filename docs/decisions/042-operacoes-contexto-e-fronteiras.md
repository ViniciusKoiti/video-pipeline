# ADR 042 — Operações separadas, contexto e fronteiras entre camadas

Data: 2026-11-01. Status: aceita nas partes verificadas por teste (`Context`, `Settings`, registro de comandos,
orquestração); **proposta** nas operações `voice`, `subs`, `render` e em `EpisodeFolder`, que ainda não existem.
RF4 do [fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md); gaps G06–G09 da
análise de gaps de 2026-10-31 (removida; o resumo está em [refatoracao-resultado](../refatoracao-resultado-2026-11-01.md), §4 e §7).

## Decisão (verificada)

- **`Context` declara o que o CLI e os scripts usam.** Entraram `tts_final`, `tts_named` e `word_aligner`, que o
  `LazyContext` já tinha e a porta e o `FakeContext` não. `tests/test_context_contract.py` confere que as duas
  implementações têm todos os membros declarados e que tudo o que o `app/` e os `scripts/` leem de
  `context`/`ctx` está declarado. O `FakeContext` imita o real: `tts_final` cai em `tts` e nome de voz
  desconhecido é `ConfigurationError`.
- **O núcleo não lê `Settings`.** `app.pipeline` (menos `ports.py`, que só declara `Context.settings`),
  `app.media`, `app.render` e `app.storage` não importam `app.settings`. A composição e o CLI resolvem a
  configuração e entregam aos serviços portas e valores. Guarda em `tests/test_architecture.py`.
- **Contratos compartilhados não carregam a orquestração.** `app.pipeline.production` e `app.pipeline.short`
  (os orquestradores dos fluxos longo e Short, ainda por criar) só podem ser importados por `app.cli`,
  `app.bootstrap` e `app.commands`. Tradução, SFX, medição e a mídia (earshot) medem e conferem sem o ciclo de
  produção. O guarda vale desde já, antes de os módulos existirem.
- **Registro de comandos explícito.** Todo handler entra em `HANDLERS` por import; o teste proíbe
  `import_module`, `pkgutil` e `__import__` em `app/cli.py` e `app/commands/`. `importlib.metadata` (a versão do
  pacote) é permitido. Comando sem handler sai com 3; argumento faltando, com 2 (argparse).

## Proposta (a provar quando as operações forem implementadas, RF6)

| Operação | Entrada persistida | Não pode |
|---|---|---|
| `voice` | `scenes.json` válido, glossário; só isso | ler ativos, escrever `episode.json` ou legendas, alinhar palavras, renderizar |
| `subs` | WAVs íntegros e `scenes.json` | sintetizar voz, chamar alinhador remoto sem pedido do dono (ADR 023) |
| `render` | `episode.json`, WAVs e ativos aprovados | sintetizar voz, alinhar |

- Cada operação confere as pré-condições dela sob o lock do episódio e funciona num processo novo, só com
  arquivos persistidos; nada depende de método chamado antes na mesma instância. A voz de rascunho não exige
  ativos escolhidos. Um `run()` que faz tudo só entra com uso concreto.
- Voz final e prévia vs. final são intenções separadas: a voz vem de `tts_final`, o tamanho do vídeo vem do
  render. Condições propostas: voz final pede `scenes.json` sem erro no `vp check`; render final pede todos os
  ativos dos planos aprovados (gate 3), todos os WAVs íntegros e o `episode.json` montado.
- **`EpisodeFolder`** localiza e acessa artefatos (layout, leitura de schemas, lock). A política de proteção é
  do fluxo de escrita (`WriteGuard`, ADR 039) e a preparação do pacote de vídeo e texto é da operação de saída;
  a pasta não delega função de outros módulos. Quem escreve consulta o guard.
- O plano de revisão de áudio (`AudioReviewPlan`) é montado na camada que conhece os formatos de produção; a
  mídia recebe cortes e expectativas prontos.
