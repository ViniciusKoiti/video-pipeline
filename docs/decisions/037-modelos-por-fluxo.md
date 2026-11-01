# ADR 037 — Modelos de dados por área

Data: 2026-11-01. Status: aceita, por pedido do dono nesta sessão.

## Contexto

Objetos de dados estavam misturados com comandos, etapas e adapters. A separação inicial de
`BenchClaim` e `BenchScript` deve valer para todos os fluxos, com um lugar previsível para cada modelo.

## Decisão

- Modelos ficam em `app/<área>/models/<nome_em_snake_case>.py`, com uma classe por arquivo.
  Exemplos: `app/pipeline/models/bench_claim.py`, `app/media/models/caption_word.py` e
  `app/providers/tts/models/speech_result.py`. Subáreas de provedores mantêm seus próprios `models/`.
- São modelos os objetos Pydantic, dataclasses, enums e TypedDicts, inclusive suas bases privadas.
  Seus validadores permanecem junto dos dados. Serviços, adapters, comandos executáveis, exceções e
  `Protocol`s permanecem nos módulos de execução, erros e portas.
- Tipos, constantes e funções puras usados pelos modelos podem ficar em módulos auxiliares dessa pasta.
  Não se cria uma pasta vazia para uma área que ainda não tem modelos. Não se acrescenta I/O aos modelos.
- Dependências entre modelos usam o módulo específico. Os `__init__.py` de `models/` ficam mínimos,
  evitando carregar todos os modelos ou criar ciclos por uma importação agregada.
- Não há catálogo global em `app/models/`: os arquivos anteriores ali são apenas compatibilidade.
  Os módulos de origem também reexportam os nomes existentes para preservar consumidores, scripts e testes.
  Código novo importa os modelos pelo caminho da área.
- `app.settings` e `app.bootstrap` tornam-se pacotes para abrigar seus modelos. Os imports públicos
  existentes continuam válidos; carregamento de configuração e composição continuam fora de `models/`.

## Aplicação e verificação

Foram movidas 183 classes de dados de 36 módulos, incluindo pipeline, mídia, provedores, render,
comandos, configuração e composição. A comparação dos 133 schemas Pydantic antes e depois da mudança
não encontrou diferenças; a migração não exige regravar JSON de episódios.

`tests/test_model_layout.py`, executado pelo gate de qualidade, verifica localização, herança,
aliases de importação e uma classe por arquivo. A guarda de arquitetura permite importar contratos
em `models/`, mantendo as restrições sobre adapters concretos e orquestração. A tipagem estrita e os
testes de comportamento continuam obrigatórios.

## Consequências

Há mais arquivos, mas cada modelo passa a ter uma origem definida. Reexports são uma transição
compatível, não um segundo local de definição. A guarda usa análise estática de classes e imports;
não reconhece modelos criados dinamicamente nem prova responsabilidade única ou ausência de I/O.
A organização complementa SOLID; a divisão de serviços extensos e os demais gaps seguem no fluxo RF1–RF7.
