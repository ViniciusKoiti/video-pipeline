# Instruções do workspace

Leia [CLAUDE.md](CLAUDE.md) antes de trabalhar neste repositório. Ele contém o contexto,
os limites de cada papel, as skills locais e os comandos disponíveis. Carregue somente
a skill e as referências pertinentes à tarefa. As instruções explícitas do dono prevalecem.

Modelos de dados de todos os fluxos ficam em `app/<área>/models/`, uma classe por arquivo
([ADR 037](docs/decisions/037-modelos-por-fluxo.md)). Serviços, adapters e portas mantêm seus módulos próprios.
Código novo importa modelos pelo módulo da área; reexports antigos existem para compatibilidade.
O gate de qualidade verifica essa organização em `tests/test_model_layout.py`.

Grupos de constantes operacionais usam classes em `app/<área>/constants/`, com atributos tipados
como `Final` e coleções imutáveis ([ADR 038](docs/decisions/038-constantes-por-area.md)).
Essa regra vale em todo `app/`, inclusive para constantes privadas e de validação; o gate a verifica em
`tests/test_constants_layout.py`, incluindo imutabilidade de coleções aninhadas. Campos de modelos, aliases
de tipos, variáveis locais e os dois registros mutáveis de composição documentados na ADR mantêm seu papel.

<!-- codebase-memory-mcp:start -->
For structural codebase exploration, use the installed `codebase-memory` skill.
<!-- codebase-memory-mcp:end -->

Use o projeto `home-viniciusk-projetos-auto-play` no grafo (raiz deste workspace).
Confira `list_projects` e `index_status` antes de
consultas estruturais; valide os caminhos relevantes com `check_index_coverage` e leia
a fonte quando houver lacuna ou resultado desatualizado. Sem ferramentas MCP na sessão,
use a CLI instalada conforme [o guia local](docs/opencode-codebase-memory-mcp.md).
