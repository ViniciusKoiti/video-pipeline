# 006 — Arquitetura: portas (Protocols) e adaptadores trocáveis

- **Status:** aceito
- **Data:** 2026-09-25
- **Etapa do roadmap:** #4

## Contexto

A Fase 0 compara três motores de render, e o §7 prevê trocar provedores de texto, voz e imagem após
benchmarks. Sem um contrato comum, cada troca reescreveria as etapas do pipeline. A spec proíbe framework
de injeção de dependência, plugin loader e dependências novas sem motivo (§2.8, §2.9).

## Decisão

1. **Uma porta (`typing.Protocol`) por função, junto de quem a implementa:** `providers/<função>/base.py`
   (`TextProvider`, `TTSProvider`, `ImageGenProvider`, `ArchiveProvider`, `SubtitleAligner`),
   `render/base.py` (`RenderEngine`) e `pipeline/ports.py` (`ManifestStore`, `ReviewGate`, `Context`).
   Chamadas síncronas: o pipeline faz uma coisa por vez (§3).
2. **A porta de texto é só transporte:** `generate_json(TextRequest[T]) -> TextResult[T]`, com o schema
   pydantic da saída. `generate_script()` e `generate_scenes()` do §7 passam a ser funções do pipeline que
   usam essa porta. Prompts, trechos-fonte e validação de claims ficam num lugar só, e trocar Ollama por
   Gemini muda apenas o adapter.
3. **Raiz de composição única (`app/bootstrap.py`)** com registro explícito nome → fábrica. As fábricas
   importam o adapter dentro da função, e o `LazyContext` monta cada porta no primeiro uso: `vp status`
   não carrega PyTorch. Nome desconhecido em `config/providers.toml` falha na hora, com as opções; adapter
   ainda não implementado informa a etapa do roadmap.
4. **Configuração:** `config/providers.toml` escolhe a implementação de cada função (a lista `archives` é
   a ordem da cascata) e guarda parâmetros sem segredo, como `num_thread = 8`. Ambiente > `.env` > toml
   para as variáveis do §3; segredos só do ambiente, em `SecretStr`. O toml com `[secrets]` é recusado.
5. **Trava de custo na arquitetura (§2.1):** todo adapter declara `ProviderInfo(name, remote,
   usd_per_call)`. A raiz de composição recusa custo > 0 (`PaidApiBlocked`) sem `ALLOW_PAID_API=true` **e**
   `MAX_API_SPEND_USD > 0`. `ImageGenProvider.estimate_cost` cobre o custo por chamada variável.
6. **Falha para a cena, não o episódio:** `ProviderError` e subclasses (`QuotaExhausted`,
   `ModelUnavailable`, `LicenseUnknown`, `InvalidOutput`, `PaidApiBlocked`) viram `needs_review` só na
   cena, via `pipeline.failures.for_each_scene`. Outras exceções são bugs e sobem.
7. **CLI em `app/cli.py`** (antes em `app/pipeline/cli.py`): o ponto de entrada monta o contexto e chama
   as etapas; o pipeline não pode importar a raiz de composição.
8. **Fakes em `tests/fakes/` e testes de contrato em `tests/test_contracts.py`:** uma lista por porta; todo
   adapter real entra na lista e passa nos mesmos testes, sem rede.

## Consequências

- Regras de dependência verificadas por `tests/test_architecture.py` (análise estática com `ast`).
- O MVP continua com uma implementação por função em uso; a porta existe para trocar, não para rodar
  várias ao mesmo tempo (§2.8).
- Diagrama e passo a passo em `docs/arquitetura.md`.
- Sem dependência nova: `tomllib`, `wave`, `ast` e `functools` são da biblioteca padrão.
