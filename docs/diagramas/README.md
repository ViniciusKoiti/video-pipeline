# Diagramas

Pastas `puml/`, `mermaid/` e `svg/`. Uma fonte por saída, com o mesmo nome: `puml/<nome>.puml` gera
`svg/<nome>.svg`, e `mermaid/<nome>.mmd` (ou `.mermaid`) também. Nenhum SVG fica sem fonte. Ao mudar um
diagrama, regenerar a saída no mesmo commit.

| Diagrama | Fonte | Saída | Assunto | Situação |
|---|---|---|---|---|
| `arquitetura-atual` | `puml/arquitetura-atual.puml` | `svg/arquitetura-atual.svg` | Arquitetura implementada | **Defasado**: árvore de 22/10 (base `313d718`), anterior ao RF1–RF7. Redesenhar ao fim do RF7 (`docs/plano-organizacao-docs-2026-11-01.md`, fase E) |
| `pipeline-hoje` | `mermaid/pipeline-hoje.mermaid` | (sem saída; o GitHub e o GitLab renderizam o Mermaid) | Fluxo do longo e do Short, em três faixas, com as lacunas marcadas | 2026-10-31; as lacunas de comandos mudaram com o RF7 |
| `pipeline-plano-2026-09-26` | `mermaid/pipeline-plano-2026-09-26.mermaid` | (idem) | Fluxo originalmente planejado | Histórico, não se atualiza |

## Gerar

- **PlantUML**: os diagramas usam `!pragma layout smetana`, que dispensa o Graphviz. Comando esperado:
  `plantuml -tsvg -o ../svg puml/<nome>.puml`.
- **Mermaid**: `mmdc -i mermaid/<nome>.mmd -o svg/<nome>.svg` (Mermaid CLI).

Não conferi estes dois comandos nesta máquina: há só o Java, sem `plantuml` nem `mmdc` instalados. Os SVGs
atuais foram gerados antes e não foram regerados na reorganização de 2026-11-01.
