# Codebase-memory no workspace de vídeo

Configuração conferida em **13/10/2026**, com o binário instalado **0.11.0**.
A ferramenta faz exploração estrutural do código; não gera voz, renderiza vídeos,
verifica fatos do roteiro ou aprova gates.

## Estado configurado

- Binário: `/home/viniciusk/.local/bin/codebase-memory-mcp`.
- Projeto do grafo usado pelo MCP: `home-viniciusk-projetos-auto-play`.
- Raiz indexada: `/home/viniciusk/projetos/auto-play`.
- MCP já registrado globalmente no Codex e no Claude; não foi reinstalado.
- Skill global `codebase-memory` disponível; [AGENTS.md](../AGENTS.md) orienta seu uso.
- [CLAUDE.md](../CLAUDE.md) explica os limites do grafo no trabalho editorial.
- Índice criado em modo `full`, usando o cache padrão fora do repositório.
- [Exclusões locais](../.cbmignore) versionáveis e diretório de export opcional
  `.codebase-memory/` ignorado pelo Git.
- [Mapeamento local de extensão](../.codebase-memory.json): `.MD` como Markdown,
  necessário para incluir `CLAUDE.md` na versão instalada.

No início da configuração, as ferramentas MCP não estavam expostas e a CLI foi
usada como alternativa. Na retomada, o servidor já estava disponível nesta sessão:
indexação, busca, rastreamento e leitura de código foram validados diretamente por MCP.
Reinicie apenas clientes que ainda não mostrem as ferramentas registradas.

O primeiro índice pela CLI recebeu o alias `auto-play`; o MCP usa o nome derivado
da raiz mostrado acima. As instruções e exemplos usam o índice ativo do MCP.
O alias `auto-play` ficou sem atualização e foi apagado em 13/10/2026; a versão
instalada ignora `--name` e grava sempre com o nome derivado da raiz.

Não foi criada uma entrada local duplicada de servidor, nem alterado o comportamento
global de indexação automática. Este guia substitui a proposta anterior de instalação
somente no OpenCode. A configuração do OpenCode não foi alterada nesta tarefa.

## O que entra e o que fica fora

O índice cobre código Python (`app/`, `scripts/`, `tests/`), template TS/TSX
(`video/src/`), scripts JavaScript/MJS, configuração, documentação e instruções
de agentes. As skills e agentes em `.claude/` são incluídos explicitamente; as
configurações privadas dessa pasta continuam excluídas.

Não entram `data/`, `renders/`, sprites brutos, ambientes virtuais, dependências,
caches, arquivos `.env*`, chaves e configurações privadas. Fixtures de código e
contratos em `tests/fixtures/` continuam disponíveis; binários podem ser excluídos
pelos filtros do próprio indexador.

O arquivo `.cbmignore` controla apenas indexação, sem mudar o que o Git versiona.
Esse comportamento e a sintaxe estão na [documentação da versão 0.11.0](https://github.com/DeusData/codebase-memory-mcp/blob/v0.11.0/docs/cbmignore.md).

## Uso diário

Antes de explorar:

```bash
codebase-memory-mcp cli list_projects
codebase-memory-mcp cli index_status --project home-viniciusk-projetos-auto-play --diagnostics summary
codebase-memory-mcp cli get_graph_schema --project home-viniciusk-projetos-auto-play
```

Atualizar o índice da árvore de trabalho:

```bash
codebase-memory-mcp cli index_repository --repo-path /home/viniciusk/projetos/auto-play --name home-viniciusk-projetos-auto-play --mode full
```

Execute novamente depois de mudanças quando não houver acompanhamento por uma sessão
MCP ativa. Não presuma que uma indexação feita pela CLI mantém um watcher permanente.
A exportação `--persistence true` é opcional e não foi ativada.

Localizar símbolos de validação, render e voz:

```bash
codebase-memory-mcp cli search_graph --project home-viniciusk-projetos-auto-play --name-pattern '^(check_episode|scene_props|KeywordShot|radar_dir|SubprocessWorker)$' --limit 20
```

Rastrear chamadas e ler a implementação descoberta:

```bash
codebase-memory-mcp cli trace_path --project home-viniciusk-projetos-auto-play --function-name home-viniciusk-projetos-auto-play.app.pipeline.check.check_episode --direction both --depth 1 --limit 50
codebase-memory-mcp cli get_code_snippet --project home-viniciusk-projetos-auto-play --qualified-name home-viniciusk-projetos-auto-play.app.pipeline.check.check_episode --source-mode full
```

Conferir cobertura antes de usar resultados como evidência:

```bash
codebase-memory-mcp cli check_index_coverage --project home-viniciusk-projetos-auto-play --paths '["app/pipeline/check.py","app/render/remotion.py","video/src/Editorial.tsx"]' --diagnostics full
```

Use a ajuda da versão instalada para outras flags:

```bash
codebase-memory-mcp cli search_graph --help
codebase-memory-mcp cli trace_path --help
codebase-memory-mcp cli check_index_coverage --help
```

Resultados paginados precisam de continuação quando houver `has_more` ou cursor.
Cobertura sem lacuna registrada não prova que toda chamada dinâmica foi resolvida.
Não classifique uma função como inútil só por não encontrar callers no grafo.

## Projetos vizinhos e fronteiras

`motion-kit/`, `lab-voz/` e `radar-de-reels/` estão ao lado do auto-play.
Na retomada, `list_projects` também retornou `home-viniciusk-projetos-motion-kit`
e `home-viniciusk-projetos-radar-de-reels`, já indexados por outras sessões.
Lab-voz não apareceu nessa lista. Consultas com um único `project` não percorrem
automaticamente o código de todos eles; a cobertura dos vizinhos não foi auditada aqui.

- **Motion-kit:** o template importa o pacote fixado em `video/package.json`;
  `node_modules` fica fora do índice. Conferir API e SHA no pacote/checkout quando
  a alteração depender de código da biblioteca.
- **Radar:** a integração copia um JSON e lê o brief do episódio; essa transferência
  não deve ser tratada como uma chamada direta entre funções dos dois repositórios.
- **Lab-voz:** o adapter executa um worker com Python externo configurado; o grafo
  do auto-play não comprova o valor atual de `CHATTERBOX_PYTHON`.

O [mapa do workspace](WORKSPACE-ATUAL-E-COMPONENTES.md) descreve essas integrações.
Indexar projetos vizinhos separadamente pode ajudar uma análise posterior; isso
não substitui a revisão dos imports, arquivos transferidos e caminhos configurados.

## Verificação e limitações observadas

A indexação inicial foi concluída e as consultas localizaram `check_episode`,
`RemotionEngine.scene_props`, `KeywordShot`, `radar_dir` e `SubprocessWorker`.
Busca por símbolos Python/TSX, rastreamento de callers/callees, snippets e outline
do script MJS foram testados por MCP. A validação final também confere a cobertura
de código e instruções incluídos.

Os caminhos Python, TSX, MJS e as skills consultados tiveram cobertura com
`metadata_match`, sem problema registrado. As lacunas dos escopos de código
conferidos foram caches Python e arquivos gráficos/fontes excluídos intencionalmente.
Após mapear `.MD`, `CLAUDE.md` também passou a ter `metadata_match`.
Isso confirma a configuração consultada, sem provar resolução de toda chamada dinâmica.

O parser 0.11.0 reportou falha em `docs/pipeline-flowchart.mermaid` e
`docs/pipeline-hoje.mermaid`. Os arquivos continuam no repositório; leia os
diagramas diretamente e não use o grafo como prova da sua interpretação.
Arquivos excluídos intencionalmente também não podem ser usados como evidência
a partir de uma busca vazia.

O sandbox desta sessão não permitiu a gravação/manutenção do cache em
`~/.cache/codebase-memory-mcp`; as chamadas necessárias da CLI receberam
escalonamento. O cache não foi desviado para um índice paralelo temporário.

Referência de configuração da versão instalada:
[DeusData/codebase-memory-mcp 0.11.0](https://github.com/DeusData/codebase-memory-mcp/blob/v0.11.0/docs/CONFIGURATION.md).
