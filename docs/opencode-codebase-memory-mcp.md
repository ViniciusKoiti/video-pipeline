# codebase-memory-mcp no opencode

Como ligar o [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) ao opencode nesta máquina
(WSL2/Ubuntu, opencode 1.17.8, config global em `~/.config/opencode/opencode.jsonc`).

Fonte: README do projeto, consultado em 2026-10-11. Nada aqui foi instalado ou testado ainda.

## O que é

Um servidor MCP que indexa o repositório num grafo (funções, classes, chamadas, imports, rotas) e responde a
consultas estruturais: quem chama uma função, o que um diff afeta, visão geral da arquitetura. O agente consulta
o grafo em vez de abrir arquivo por arquivo.

- Licença MIT, binário nativo, sem Docker, sem runtime e sem chave de API.
- Roda 100% local; o README afirma que o binário não faz requisição de rede por conta própria.
- Custo zero, e não entra no `pyproject.toml` nem no `video/package.json`: é ferramenta da máquina, não
  dependência do projeto.

## Escolha antes de instalar

O comando `install` do projeto configura **todos** os agentes que ele detecta na máquina, não só o opencode.
Aqui isso inclui o Claude Code: ele escreveria entrada de MCP, skill, instruções e hooks também lá.

| Caminho | O que muda | Quando usar |
|---|---|---|
| A. Só o opencode (manual) | Uma entrada `mcp` no `opencode.jsonc` | Quer testar sem mexer no Claude Code |
| B. Instalador completo | MCP + `AGENTS.md` + skill + 3 agentes só-leitura + plugin no opencode, e o equivalente nos outros agentes detectados | Quer a integração inteira em tudo |

Recomendação: começar pelo A. Dá para rodar o B depois.

## Caminho A: só o opencode

### 1. Baixar o binário sem configurar agentes

```bash
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh -o /tmp/cbm-install.sh
less /tmp/cbm-install.sh                 # opcional: ler antes de rodar
bash /tmp/cbm-install.sh --skip-config   # só o binário, nenhum agente configurado
```

`--dir=<caminho>` escolhe outra pasta de instalação. Depois, anote o caminho absoluto:

```bash
which codebase-memory-mcp
codebase-memory-mcp --version
```

### 2. Registrar no opencode

Em `~/.config/opencode/opencode.jsonc` (vale para todos os projetos) ou num `opencode.json` na raiz deste
repositório (vale só aqui):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "codebase-memory-mcp": {
      "type": "local",
      "command": ["/caminho/absoluto/codebase-memory-mcp"],
      "enabled": true
    }
  }
}
```

Troque o caminho pelo que o `which` devolveu. No opencode, `command` é uma lista (binário + argumentos), e o
bloco se chama `mcp`, não `mcpServers` como no exemplo do README (que é do Claude Code).

### 3. Conferir

```bash
opencode mcp list
```

O servidor deve aparecer como conectado. Reinicie o opencode se ele já estava aberto.

## Caminho B: instalador completo

```bash
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
```

No opencode ele escreve em `$OPENCODE_CONFIG` ou na config global e acrescenta `AGENTS.md`, uma skill, três
agentes só-leitura e um plugin (consulta ao grafo em grep/glob, contexto no início da sessão e depois da
compactação). Reinicie todos os agentes abertos ao terminar.

## Indexar este repositório

Dentro do opencode, peça: **"Index this project"**. Ou pelo terminal:

```bash
codebase-memory-mcp cli index_repository --repo-path ~/projetos/auto-play
codebase-memory-mcp cli list_projects
```

Use o `name` devolvido por `list_projects` como `--project` nas consultas.

Opcional, para indexar sozinho ao abrir a sessão:

```bash
codebase-memory-mcp config set auto_index true
```

O índice fica em `~/.cache/codebase-memory-mcp` (ou `$CBM_CACHE_DIR`), fora do repositório. Projetos git são
acompanhados por um daemon em segundo plano enquanto houver sessão aberta; `config set auto_watch false` desliga
esse acompanhamento por sessão.

## Ferramentas mais úteis

| Ferramenta | Para quê |
|---|---|
| `get_architecture` | Visão geral: linguagens, pacotes, pontos quentes |
| `get_graph_schema` | Contagem de nós e arestas; rodar primeiro |
| `search_graph` | Busca estrutural e semântica por símbolo |
| `trace_path` | Quem chama uma função e o que ela chama |
| `detect_changes` | Símbolos afetados por um diff do git |
| `get_code_snippet` | Código de uma função pelo nome qualificado |
| `search_code` | Busca de texto nos arquivos indexados |
| `query_graph` | Consulta Cypher só-leitura |

Exemplos pelo terminal:

```bash
codebase-memory-mcp cli search_graph --project <nome> --name-pattern '.*check.*' --label Function
codebase-memory-mcp cli trace_path --project <nome> --function-name cpu_probe --direction both
```

`codebase-memory-mcp cli <ferramenta> --help` lista os parâmetros de cada uma.

## Interface gráfica (opcional)

```bash
codebase-memory-mcp --ui=true --port=9749
```

Abre em `http://127.0.0.1:9749`.

## Atualizar e remover

```bash
codebase-memory-mcp update      # imprime o comando do install.sh a rodar
codebase-memory-mcp uninstall   # remove binário e entradas que ele criou; mantém os índices
codebase-memory-mcp uninstall --dry-run --delete-indexes   # mostra o que apagaria, sem apagar
```

No caminho A, apague também à mão o bloco `mcp` do `opencode.jsonc`.

## Pontos a conferir na primeira vez

- A indexação de um repositório grande usa CPU; com a máquina limitada (CLAUDE.md §3), deixe para quando ela
  estiver livre.
- Confira com `list_projects` o tamanho do índice: `data/`, `renders/` e `video/node_modules` não deveriam
  entrar. O indexador tem regras próprias de exclusão, que não foram verificadas aqui.
- Se uma chamada de `index_repository` estourar o tempo do cliente, use `async: true` e acompanhe com
  `status: true`.
