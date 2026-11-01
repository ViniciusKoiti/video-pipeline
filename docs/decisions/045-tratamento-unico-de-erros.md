# ADR 045 — Tratamento único de erros esperados na borda

Data: 2026-11-01. Status: aceita, por pedido do dono nesta sessão (RF5-bis do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md)).

## Contexto

Os erros esperados do projeto (episódio travado, gate que não vale, fonte sem texto, provedor sem cota) eram
capturados por listas de tipos escritas à mão em 7 pontos de comandos e scripts, cada uma diferente: `vp
approve` e `vp reopen` não capturavam `ImmutableManifest`, que os scripts de fonte capturavam. As 31 classes
de erro tinham 5 bases diferentes (`ValueError`, `RuntimeError`, `LookupError`, `PermissionError`,
`Exception`), então ninguém conseguia capturar "erro do projeto" de uma vez. Eram 53 `raise SystemExit(...)`
com formatos de mensagem diferentes, e `cli.py` capturava `KeyError` e `TypeError`, que são bugs.

## Decisão

- **`app.errors.PipelineError`**, módulo sem dependências que qualquer camada importa. Toda classe de erro de
  `app/` herda dela, junto com a base de antes (`class GateError(PipelineError, ValueError)`), então nenhum
  `except ValueError` existente deixou de pegá-la. `ProviderError` e `TransportError` entram na árvore, e as
  subclasses de `ProviderError` herdam sozinhas.
- **Um handler só**, `app.commands.errors.run(rótulo, ação)`: captura só `PipelineError`, imprime
  `<rótulo>: <mensagem>` no stderr e devolve 1 (`CliConstants.EXIT_ERROR`). O `main()` do CLI usa `vp <comando>`
  como rótulo; os scripts usam `raise SystemExit(run("nome", main))`. Comandos e scripts não têm `try/except` de
  erro do projeto: levantam. Retorno `None` é 0; o código de saída de uma ação bem-sucedida é mantido.
- **Bug continua com traceback** (§2.1): o handler nunca captura `Exception` solta. Com `VP_DEBUG` definido, o
  erro tratado também sobe com o traceback inteiro.
- **Tradução na entrada, não tratamento no comando:** o parecer do verificador, escrito à mão, é lido por
  `load_check_report`, que transforma arquivo ausente ou fora do formato em `GateError`. O `try/except` de
  `OSError`/`ValueError`/`KeyError`/`TypeError` mora ali, uma vez.
- **A recuperação continua onde é possível:** `for_each_scene`, `run_scenes`, `search_archives` e o laço por
  ativo de `baixar_escolhidos` (`except PipelineError`, o erro de um ativo não para os outros).
- **Fica como está:** `postiz` e `usage` têm contrato de erro em JSON, com mensagens fixas que não vazam
  segredo; `postiz_cadeia` registra a falha do agendamento na trilha e relança; `montar_episodio.py` e
  `shorts_tec.py` têm o fallback e a parada da voz, que migram com o `Narrator` (RF6).
- **Gate** (`tests/test_errors_layout.py`): toda classe de exceção de `app/` herda de `PipelineError`; comandos e
  scripts não capturam erro do projeto por tipo, salvo a lista `ALLOWED`, com o motivo de cada arquivo. A lista
  só encolhe: o teste falha se um arquivo dela deixou de ter o `except`.
- **Códigos de saída:** continuam 1 (erro tratado), 2 (uso incorreto, argparse) e 3 (comando não implementado).
  Códigos distintos por tipo (episódio travado, cota) ficam para quando a rotina diária (ADR 036) precisar.

## Consequências

A mensagem de um erro tratado em script perde o prefixo do id do episódio que alguns tinham; as mensagens dos
erros do projeto já trazem o episódio e o arquivo (`ep/sources.json está carimbado...`).

## Emenda de 2026-11-01 (manifesto fora do contrato)

Um `scenes.json` (ou qualquer manifesto) editado à mão e fora do schema saía com o traceback do pydantic, fora do
tratamento central. `JsonFileStore.read` agora converte o `ValidationError` em `ManifestInvalid` (um
`PipelineError` e `ValueError`, em `app/pipeline/ports.py`): `vp <comando>: <episódio>/<arquivo> fora do contrato:
<campo>: <motivo>`, com os cinco primeiros campos e o erro original na cadeia (`VP_DEBUG` mostra). Erro na raiz do
arquivo (JSON cortado, lista no lugar de objeto) sai como `(arquivo)`. Quem lia o manifesto e tratava
`ValidationError` (`vp check`, a lista de ativos e a conferência de aprovação do render final) passou a tratar
`ManifestInvalid`, com o mesmo resultado. O que não passa pelo store (`ValidationError` ao montar um modelo no
código) continua sendo bug, com traceback.
