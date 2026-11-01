# Plano de organização do `docs/` (2026-11-01)

Pedido do dono: reunir os diagramas em uma pasta (fonte `.puml` e `.svg`) e remover os `.md` desatualizados.

## 1. Diagnóstico

| Achado | Dado |
|---|---|
| Arquivos em `docs/` fora de `decisions/` e `pesquisa/` | 31 `.md` (23 na raiz, 6 em `specs/`, 2 em `tarefas/`), 4 `.puml`, 8 `.svg`, 3 `.mmd`, 3 `.png` de diagrama, 1 `.mermaid`, 2 `.png` de sprite e 2 `.mp3` |
| Diagramas espalhados | `.puml` e `.svg` soltos na raiz, `diagramas-consumo/` com Mermaid + PNG + SVG, `pipeline-hoje.mermaid` na raiz e `pipeline-plano-2026-09-26.mermaid` dentro de `pesquisa/` |
| Diagrama sem consumidor | `execucao-proposta.svg` é o 2º diagrama de `classes-e-integracao.puml` e só o `evolucao-por-camadas.md` o cita |
| Fotografias datadas tratadas como atuais | 7 documentos de 24/09 a 22/10 descrevem o `app/` de antes do RF1–RF6; ao menos 4 documentos citam arquivos que já não existem (`app/pipeline/production.py`, `app/pipeline/retrieval.py`, `docs/spec-v0.4.md`, `docs/pipeline-flowchart.mermaid`) |
| Índice | a seção de docs do `README.md` lista 13 destes arquivos sem dizer quais são fotografia e quais são guia |
| Mídia do dono em `docs/` | `A Planilha é Tua.mp3` e `A Vinha Não é Sua (1).mp3` (fora do Git pelo `.gitignore`); `kenny-sprite.png` e `person-sprite.png` (commitados em 2026-11-01) |

Critério de "desatualizado": o documento é uma **fotografia datada** (análise ou proposta de um dia), foi **superado** por ADR, código ou documento mais novo, e **não tem consumidor ativo** (código, testes, skill, agente ou `CLAUDE.md`). O que tem consumidor ativo fica até o consumidor ser trocado. ADRs nunca saem: são o registro de decisão.

## 2. Estrutura-alvo

```
docs/
  README.md                  índice único, com o papel de cada documento (substitui a lista do README da raiz)
  decisions/                 ADRs (não muda)
  diagramas/
    README.md                como cada diagrama é gerado e quando foi conferido
    puml/                    fonte PlantUML
    mermaid/                 fonte Mermaid (.mmd e .mermaid)
    svg/                     saída vetorial, com o mesmo nome da fonte
  specs/  pesquisa/  ROADMAP.md  e os guias atuais (postiz, usage, gate-qualidade, arquitetura, ...)
```

A regra da pasta de diagramas: **um `.puml` ou `.mmd` por `.svg`, com o mesmo nome**, e nenhum SVG sem fonte. Exceção atual: `classes-e-integracao.puml` tem dois diagramas (`classes-e-integracao` e `execucao-proposta`); sai na fase B.

Subpastas por assunto para os guias (`guias/`, `refatoracao/`) ficam como fase opcional (D): mexem em caminhos citados pelo `CLAUDE.md`, por skills e por ADRs, e não foram pedidas.

## 3. Fases

| Fase | O que faz | Quando |
|---|---|---|
| A | Cria `docs/diagramas/` e move os diagramas (`git mv`), renomeando `diagramas-consumo/*` com o prefixo `consumo-`. Ajusta os links. | agora |
| B | Remove os `.md` da tabela "remover agora" e os diagramas que só ilustravam eles. Ajusta os links que sobrarem. | agora |
| C | Cria `docs/README.md` (índice com papel de cada arquivo) e enxuga a lista do `README.md` da raiz para apontar para ele. | agora |
| B2 | Remove o que a tabela 4.2 lista (o dono mandou tirar o que não é necessário e vital). | feita |
| D | Subpastas por assunto (opcional). | descartada |
| E | **Depois do RF7:** redesenhar `arquitetura-atual` e `pipeline-hoje` a partir do `app/` de então (comandos `vp`, serviços, portas), mover as análises do RF (`analise-gaps-solid`, `analise-scripts-provisorios`, `analise-tamanho-modulos`, `desenho-orientado-a-objetos`, `fluxo-refatoracao`, `loop-refatoracao`, `inventario-constantes`, `qualidade-tipagem`) para uma pasta de histórico e registrar a decisão. | fim do RF7 |

## 4. Classificação

### 4.1 Remover agora (fase B)

| Arquivo | Motivo | Consumidores a ajustar |
|---|---|---|
| `ANALISE.md` | Fotografia de 2026-09-24; cita `docs/spec-v0.4.md` e `docs/pipeline-flowchart.mermaid`, que não existem; as questões viraram ADRs | `README.md`; `ROADMAP.md:87`; `pesquisa/nichos-reels-animados.md:74,427` (menção histórica ao "item 18") |
| `WORKSPACE-ATUAL-E-COMPONENTES.md` | Fotografia de 13/10 da branch `objetivo-do-video`; 403 linhas sobre um estado anterior ao RF1–RF6 | `README.md`; `opencode-codebase-memory-mcp.md` |
| `analise-gaps-tecnicos.md` | Fotografia de 22/10 no commit `313d718`; superada pela `analise-gaps-solid` e pelo RF | `README.md`; `analise-scripts-provisorios`, `evolucao-por-camadas` e `arquitetura-ia` (os dois últimos saem junto) |
| `evolucao-por-camadas.md` + `fluxo-evolucao.puml/.svg` + `classes-e-integracao.puml/.svg` + `execucao-proposta.svg` (2º diagrama de `classes-e-integracao.puml`) | Proposta de 22–23/10; parte virou as ADRs 039–052 e o resto foi abandonado ou refeito; cita `app/pipeline/production.py` e `retrieval.py`, que não existem | `README.md`; `arquitetura-ia.md` |

### 4.2 Removidos por decisão do dono (fase B2, 2026-11-01)

O dono pediu para tirar o que não for necessário e vital. Saíram `arquitetura-ia.md` (+ `.puml` e `.svg`),
`analise-pipeline-agentes.md`, `analise-prompts-locais.md`, `proposta-banco-consumo-agentes.md` (+ os três diagramas
de consumo em Mermaid, SVG e PNG), `tarefas/conectar-instagram-postiz.md`, `tarefas/plano-montagem-json-cena-e-conceito.md`,
`kenny-sprite.png` e `person-sprite.png`. Consumidores ajustados: a skill `vp-engajamento` (que citava a "Medição" da
`analise-pipeline-agentes`) passou a apontar para `CLAUDE.md` §4, §6 e §12, e a agenda do clipe cita a tarefa removida.
Tudo está no histórico do Git (`git log -- docs/<arquivo>`).

### 4.3 Manter

| Arquivo | Por quê |
|---|---|
| `ROADMAP.md` | Citado pelo `CLAUDE.md` ("Etapa atual e pendências"); precisa de revisão, não de remoção |
| `arquitetura.md`, `postiz.md`, `usage.md`, `gate-qualidade.md`, `guia-animacao-de-texto.md`, `opencode-codebase-memory-mcp.md` | Guias atuais, citados pelo `CLAUDE.md` ou por skills |
| `specs/*` | Especificações de componentes, citadas por código e testes |
| `fluxo-refatoracao-solid`, `loop-refatoracao`, `inventario-constantes`, `qualidade-tipagem`, `analise-gaps-solid`, `analise-scripts-provisorios`, `analise-tamanho-modulos`, `desenho-orientado-a-objetos` | O RF7 está em andamento e os documentos se citam; arquivam na fase E |
| `pesquisa/*` | Pesquisa datada por natureza; não é "desatualizada", é registro. Fora do escopo deste plano |
| `arquitetura-atual.puml/.svg` | Defasado (22/10, base `313d718`), mas é o único diagrama da arquitetura; fica em `diagramas/` com a data visível e é redesenhado na fase E |
| `pipeline-hoje.mermaid`, `pipeline-plano-2026-09-26.mermaid` | O primeiro é o fluxo de hoje (citado pelo `CLAUDE.md`, a atualizar na fase E); o segundo é o plano original, histórico declarado |

### 4.4 Mídia do dono em `docs/`

`A Planilha é Tua.mp3` e `A Vinha Não é Sua (1).mp3` não foram apagados. A Vinha **não tem cópia em lugar nenhum**
do projeto e o registro de licença do clipe (`video/src/clipe/LICENCAS.md`) a cita, com o id do Suno; a Planilha só tem
cópia idêntica em `data/cache/` (cache). Foram movidos para `data/clipe/audio/` (fora do Git pelo `.gitignore`) e o
`LICENCAS.md` aponta para o novo caminho. Apagar de vez é decisão do dono.

## 5. Regras da execução

- Mover com `git mv` (o histórico acompanha) e remover com `git rm`: tudo recuperável pelo Git.
- Um commit por fase (B e C saíram juntos, porque as edições do `README.md` se misturam). O gate de qualidade roda em cada commit.
- Cada remoção só depois de listar os links que apontavam para o arquivo e ajustá-los; ao final, uma busca confirma que nenhum link restou apontando para arquivo removido.
- Texto histórico dentro de ADRs e pesquisa que cita um arquivo removido não é reescrito: a menção fica, com o nome do arquivo, e o Git guarda o conteúdo.

## 6. Situação (2026-11-01)

| Fase | Situação |
|---|---|
| A | Feita (`be1bcbd`): `docs/diagramas/{puml,mermaid,svg}` com o README da pasta; links ajustados |
| B | Feita (`6f4d19e`): removidos `ANALISE`, `WORKSPACE-ATUAL-E-COMPONENTES`, `analise-gaps-tecnicos`, `evolucao-por-camadas` e os diagramas que só os ilustravam. Links markdown quebrados: de 13 para 2, ambos antigos e sem relação (`../AGENT.MD` e `/fonemas/`, um falso positivo de texto) |
| C | Feita (`6f4d19e`): `docs/README.md` com o papel de cada documento |
| B2 | Feita: tabela 4.2 |
| D | Descartada: sem subpastas por assunto, para manter os caminhos citados pelo `CLAUDE.md` e pelas skills |
| E | **Parcial (2026-11-01):** `arquitetura-atual.puml` e `pipeline-hoje.mermaid` redesenhados depois do RF7. Faltam (1) regerar `svg/arquitetura-atual.svg`, que ainda é o de 22/10 (sem `plantuml` aqui) e (2) remover as análises do RF (`analise-gaps-solid`, `analise-scripts-provisorios`, `analise-tamanho-modulos`, `desenho-orientado-a-objetos`) e o `loop-refatoracao`, só depois de o dono conferir as configurações locais (critério 3 do RF7) |

Menções por nome a arquivos removidos que ficam de propósito, em texto histórico: o `nichos-reels-animados.md`
(pesquisa) cita o "item 18" do `ANALISE.md`; o `analise-scripts-provisorios` cita a `analise-gaps-tecnicos`; a legenda do
`arquitetura-atual.puml` e do SVG gerado dele cita a `analise-gaps-tecnicos.md` (o SVG não pode ser regerado aqui, sem
`plantuml`).
