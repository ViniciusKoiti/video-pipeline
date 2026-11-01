# Documentação

Índice único do `docs/`, com o papel de cada documento. Em conflito, valem os registros em
[`decisions/`](decisions/) e o [`CLAUDE.md`](../CLAUDE.md). Plano de organização desta pasta:
[`plano-organizacao-docs-2026-11-01.md`](plano-organizacao-docs-2026-11-01.md).

**Papéis:** *guia* descreve como o sistema é hoje e se mantém; *plano* está em andamento; *fotografia* é a
análise de um dia e não se atualiza (vale o que o código e os ADRs dizem hoje); *histórico* fica pelo registro.

## Guias (mantidos)

| Documento | Assunto |
|---|---|
| [arquitetura.md](arquitetura.md) | Portas e adaptadores |
| [gate-qualidade.md](gate-qualidade.md) | O gate de qualidade (lint, tipos, testes, tamanho) |
| [postiz.md](postiz.md) | Comandos do Postiz para ferramentas e agentes |
| [usage.md](usage.md) | Consumo editorial em SQLite (`vp usage`) |
| [guia-animacao-de-texto.md](guia-animacao-de-texto.md) | Animação de texto nos Reels |
| [opencode-codebase-memory-mcp.md](opencode-codebase-memory-mcp.md) | Codebase-memory no workspace |
| [ROADMAP.md](ROADMAP.md) | Etapas entregáveis; precisa de revisão |
| [specs/](specs/) | Especificações dos componentes do template e do `vp numeros` |

## Plano em andamento: refatoração SOLID (RF0–RF7)

| Documento | Papel |
|---|---|
| [fluxo-refatoracao-solid-2026-11-01.md](fluxo-refatoracao-solid-2026-11-01.md) | Gates de aceite e registro de cada fatia |
| [loop-refatoracao.md](loop-refatoracao.md) | Prompt do loop de uma iteração |
| [inventario-constantes-2026-11-01.md](inventario-constantes-2026-11-01.md) | Inventário de constantes |
| [qualidade-tipagem-2026-11-01.md](qualidade-tipagem-2026-11-01.md) | Linha de base da tipagem |

Entradas que viraram o plano (fotografias de 2026-10-31, arquivam ao fim do RF7):
[analise-gaps-solid](analise-gaps-solid-2026-10-31.md),
[analise-scripts-provisorios](analise-scripts-provisorios-2026-10-31.md),
[analise-tamanho-modulos](analise-tamanho-modulos-2026-10-31.md) e
[desenho-orientado-a-objetos](desenho-orientado-a-objetos-2026-10-31.md).

## Fotografias e propostas (não atualizam)

| Documento | Data | Situação |
|---|---|---|
| [analise-pipeline-agentes.md](analise-pipeline-agentes.md) | 12/10 | A skill `vp-engajamento` cita a "Medição" dela |
| [analise-prompts-locais.md](analise-prompts-locais.md) | 12/10 | Prompts de `prompts/local/` e limites da validação |
| [arquitetura-ia.md](arquitetura-ia.md) | 22/10 | Rascunho de apresentação; defasado |
| [proposta-banco-consumo-agentes.md](proposta-banco-consumo-agentes.md) | 31/10 | SQLite feito (ADR 032); PostgreSQL segue proposta |
| [tarefas/](tarefas/) | 15/10 e 24/10 | Tarefas datadas |

## Diagramas

Fontes e saídas em [diagramas/](diagramas/) (ver o [README da pasta](diagramas/README.md)): `puml/`,
`mermaid/`, `svg/` e `png/`. O fluxo de hoje é
[`pipeline-hoje.mermaid`](diagramas/mermaid/pipeline-hoje.mermaid).

## Decisões e pesquisa

- [decisions/](decisions/): ADRs numeradas; o registro de cada decisão.
- [pesquisa/](pesquisa/): análises de nicho, formato, plataformas e crescimento, datadas por natureza.
