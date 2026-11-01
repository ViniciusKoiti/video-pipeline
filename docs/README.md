# Documentação

Índice único do `docs/`, com o papel de cada documento. Em conflito, valem os registros em
[`decisions/`](decisions/) e o [`CLAUDE.md`](../CLAUDE.md). Plano de organização desta pasta:
[`plano-organizacao-docs-2026-11-01.md`](plano-organizacao-docs-2026-11-01.md).

**Papéis:** *guia* descreve como o sistema é hoje e se mantém; *plano* está em andamento. Análise de um dia que o
código e os ADRs já superaram não fica aqui: o Git guarda o histórico (`git log -- docs/<arquivo>`).

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

## Refatoração SOLID (RF0–RF7)

| Documento | Papel |
|---|---|
| [refatoracao-resultado-2026-11-01.md](refatoracao-resultado-2026-11-01.md) | O que ficou: estrutura, como estender, scripts → comandos, gaps fechados e o que está aberto |
| [fluxo-refatoracao-solid-2026-11-01.md](fluxo-refatoracao-solid-2026-11-01.md) | Gates de aceite e registro de cada fatia, com as provas |
| [inventario-constantes-2026-11-01.md](inventario-constantes-2026-11-01.md) | Inventário de constantes |
| [qualidade-tipagem-2026-11-01.md](qualidade-tipagem-2026-11-01.md) | Linha de base da tipagem |

## Diagramas

Fontes e saídas em [diagramas/](diagramas/) (ver o [README da pasta](diagramas/README.md)): `puml/`,
`mermaid/` e `svg/`. O fluxo de hoje é
[`pipeline-hoje.mermaid`](diagramas/mermaid/pipeline-hoje.mermaid).

## Decisões e pesquisa

- [decisions/](decisions/): ADRs numeradas; o registro de cada decisão.
- [pesquisa/](pesquisa/): análises de nicho, formato, plataformas e crescimento, datadas por natureza.
