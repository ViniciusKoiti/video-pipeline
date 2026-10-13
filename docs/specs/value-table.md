# Spec: `ValueTable` (motion-kit) e o plano `table` (template e contrato)

- **Estado:** rascunho para aprovação do dono (2026-10-07). **Nada aqui está implementado.** Onde diz **decisão aberta**, o agente não decide: pergunta ao dono. Em conflito valem `CLAUDE.md`, as ADRs e o `AGENTS.md` do kit.
- **Origem:** `docs/pesquisa/componentes-infografico-2026-10.md` (item 1 da lista) e os formatos de Reel mapeados em `docs/pesquisa/nichos-reels-animados.md` e `nichos-globais-2026-10.md`. Convenções de animação: `docs/guia-animacao-de-texto.md`.
- **Rótulos:** [F] confirmado em arquivo; [I] inferência; [H] hipótese a medir.
- **Três camadas, três PRs** (um PR por frente): **A** o componente no kit (sem contrato); **B** a emenda às ADR 011 e 014 (só texto); **C** o plano `table` no schema, no `vp check`, no adaptador e no template, com o pin novo do kit.

## 1. O que é, e o que não é

**É** uma tabela animada de linhas `rótulo | valor | nota`, em que cada valor é **texto pronto, de unidade própria**, com entrada linha a linha no ritmo da narração, uma linha opcionalmente destacada e uma barra proporcional opcional.

**Por que existe [F]:** o plano `compare` tem **exatamente dois lados** (`left` e `right`) e o `ValueCompare` do kit trabalha com **números** (rolam no `Odometer`); `BarChart` e o plano `chart` supõem **uma unidade só**, e o `ChartShot` não tem coluna de texto, nota nem unidades misturadas. Os formatos abaixo caem no vão.

**Não é:** gráfico (a barra é opcional e só vale com unidade comum), planilha (no máximo 6 linhas e 2 colunas de dado), calculadora (**a tela não calcula**: nada de soma, razão, total, variação nem conversão de moeda, ADR 011, decisão 7), nem formatador (o kit **não formata, não traduz e não arredonda** o valor: ele mostra o texto que recebe).

**Quando usar [I]:** dois valores → `compare`; série no tempo → `chart` com `line`; partes de um todo → `chart` com `share`; categorias de **mesma unidade** em que o tamanho importa → `chart` com `bar` ou `bar_horizontal`; **3 a 6 itens com unidades diferentes, com texto ou com ressalva** → `table`.

## 2. Casos de aceite (dados reais, só no template; o kit usa dados neutros)

Os três vêm de fichas já levantadas; cada um vira um teste do plano `table` (camada C).

| # | Título | Linhas (`rótulo` → `valor`) | Unidades | Barra? | Fonte |
|---|---|---|---|---|---|
| 1 | DAS do MEI em 2026, por atividade | Comércio e indústria → R$ 82,05; Serviços → R$ 86,05; Comércio e serviços → R$ 87,05 (notas: "INSS + ICMS", "INSS + ISS", "INSS + ICMS + ISS") | mesma (R$) | sim, opcional | Receita Federal, 2026-01-02 (`nichos-reels-animados.md` §6.A) |
| 2 | Imposto do autônomo nos EUA | Taxa do imposto do autônomo → 15,3%; Ganho líquido a partir do qual ele se aplica → US$ 400; Imposto devido a partir do qual há pagamentos trimestrais → US$ 1.000 | **mistas** (%, US$) | **não** | IRS, páginas lidas em 2026-10-07 (`nichos-globais-anexos/freelance-ficha.md`) |
| 3 | Visto de trabalho remoto da Espanha em 2026 | Solteiro → € 2.442; 1º dependente → € 916; Demais dependentes → € 306 (nota: "por mês") | mesma (€) | sim, opcional | MAEC (`nichos-globais-anexos/imigracao-ficha.md`; a página não mostra data) |

Outros formatos que o componente destrava [I]: taxas do Etsy e da Amazon por categoria, planos de software, metas de proteína, quem pode aconselhar em imigração.

## 3. Camada A: o componente no kit

**Onde:** `src/charts/ValueTable.tsx`, exportado em `src/charts/index.ts` como `ValueTable`, `ValueTableProps` e `ValueTableRow` (subpath `@viniciusk/motion-kit/charts`, ao lado de `ValueCompare` [F]). Convenções do `AGENTS.md`: PascalCase, tipos explícitos, `import type`, 2 espaços, aspas simples, ponto e vírgula, vírgula final.

### 3.1 API

```ts
export interface ValueTableRow {
  /** O que o valor mede, como aparece na tela. */
  label: string;
  /** Valor como aparece na tela, texto pronto ("R$ 82,05", "6,5%", "último dia de maio").
   *  O kit não formata, não traduz, não soma e nunca quebra o valor em duas linhas. */
  value: string;
  /** Nota curta sob o rótulo (condição, ressalva). Sem nota, a linha não reserva espaço para ela. */
  note?: string;
  /** Linha que a narração destaca: cor de destaque do tema, valor mais pesado e um filete à esquerda. */
  highlight?: boolean;
  /** Frame (relativo à peça) em que o destaque acende, se for depois da entrada da linha. Troca seca.
   *  Default: o da entrada da linha. Só vale com `highlight`. */
  highlightAt?: number;
  /** Comprimento da barra, em qualquer escala comum a todas as linhas (o kit só normaliza pelo maior).
   *  Ou todas as linhas têm `bar`, ou nenhuma tem: com uma só faltando, nenhuma barra é desenhada. */
  bar?: number;
}

export interface ValueTableProps {
  rows: ValueTableRow[];
  /** Cabeçalho das duas colunas, em cinza. Opcional. */
  header?: { label: string; value: string };
  /** Frame em que a primeira linha entra. Default: 0. Negativo: a tabela já está na tela (linhas assentadas). */
  at?: number;
  /** Frames entre linhas quando `rowFrames` não vem. Default: 10. */
  stagger?: number;
  /** Frame de entrada de CADA linha (relativo à peça), na ordem, para casar com a narração; substitui
   *  `at` + `stagger`. Linhas sem frame seguem o `stagger` a partir da última informada. */
  rowFrames?: number[];
  /** Entrada de cada linha: `'cut'` (num quadro), `'pop'` ou `'rise'`. Default: `'rise'`. */
  enter?: 'cut' | 'pop' | 'rise';
  /** Largura do bloco, em px de um quadro de 1080 de altura. Default: 1200. */
  width?: number;
  /** Tamanhos, em px de um quadro de 1080 de altura. Defaults: 34, 40 e 24. */
  labelSize?: number;
  valueSize?: number;
  noteSize?: number;
  /** Frame em que a tabela inteira sai (10 quadros). Sem ele, fica até o fim da `<Sequence>`. */
  exitAt?: number;
  style?: CSSProperties;
}
```

Nomes que repetem o kit [F]: `at`, `stagger` e `rowFrames` espelham `KineticHeadline` (`at`, `stagger`, `wordFrames`); `at` negativo espelha a janela do apresentador (`at={-60}` em `HostWindow.tsx`); tamanhos em px de um quadro de 1080 de altura (`useUnit`, como todas as peças do kit).

### 3.2 Comportamento

- **Layout.** Duas colunas por linha: rótulo à esquerda (`flex: 1`, até 2 linhas) e valor à direita (`white-space: nowrap`, `font-variant-numeric: tabular-nums`, alinhado à direita); nota sob o rótulo, em `theme.muted`; um filete `theme.line` entre linhas. **O espaço de todas as linhas é reservado desde o primeiro quadro** (linha ainda não entrada fica com `visibility: hidden`): a tabela não pula quando uma linha chega.
- **Entrada.** `rise`: opacidade de 0 a 1 e subida de 24 px em 14 quadros, ease-out cúbico (os valores de `useInOut` e `useAnimateIn` [F]); `cut`: aparece inteira num quadro; `pop`: opacidade e escala de **0,85** a 1 em 4 quadros, ease-out, sem quique (**decisão aberta**: a escala inicial do `pop`, 0,45, 0,85 ou ≈0,67 medida na referência). **Sem mola em linha:** a implementação usa um único auxiliar interno de entrada; quando a PR de tokens de movimento existir, ele passa a ler `cut`/`pop`/`rise` de lá, sem mudar a API.
- **Destaque.** Texto da linha em `theme.accent`, valor com peso 800, filete de 6 px à esquerda e fundo `withAlpha(theme.accent, 0.10)`. Com `highlightAt`, acende no quadro pedido (troca seca, sem transição). **O destaque nunca depende só da cor**: peso e filete também mudam [I].
- **Barra (opcional).** Faixa de 8 px sob o conteúdo da linha, de largura `bar ÷ maior bar` da largura da linha; trilho em `theme.line`, preenchimento em `theme.muted` (em `theme.accent` na linha destacada). Cresce junto com a entrada da linha (acompanha o progresso de `enter`; com `cut`, aparece cheia). **O número da barra só dá geometria**: o kit não o exibe nem o deriva do texto.
- **Tema.** Só `useMotionTheme()` (`text`, `muted`, `accent`, `line`, `font`) e `withAlpha`; **nenhuma cor escrita no componente**, para que um preset claro futuro funcione sem mexer nele (o template de hoje esbarra em véus escuros fixos, ver `estilos-por-vertical-2026-10.md`).
- **Determinismo e custo.** Só `useCurrentFrame`; sem `Math.random`, sem `Date`. Sem filtro SVG, sem `blur` e sem sombra difusa: o custo de render é o de texto e de poucos `div` [I].
- **Bordas.** Zero linhas: não desenha nada. Uma linha: desenha (o contrato é que exige 2 ou mais). `rowFrames` menor que `rows`: o resto segue o `stagger`. Valor mais largo que a coluna: a coluna do valor cresce e a do rótulo encolhe; o alerta vem do `vp check` (seção 5), não de um corte silencioso: **falha visível é melhor que texto cortado**.
- **Fora de escopo da v1:** contagem rolando (`Odometer`) nos valores, ordenação, rolagem, mais de 2 colunas de dado, visual de painel de partidas (**`look="board"`, a v2, é o `DeadlineBoard`**: mesma API, outro visual; o nome fica reservado, sem prop agora).

### 3.3 Entregáveis da camada A

| Item | Onde | Regra |
|---|---|---|
| Componente | `src/charts/ValueTable.tsx`, com cabeçalho `@reusable` e `@example` | em português, no estilo das outras peças |
| Exportação | `src/charts/index.ts` | `ValueTable`, `ValueTableProps`, `ValueTableRow` |
| Catálogo | linha em `src/COMPONENTS.md`, na tabela de `charts` | o `describe_component` lê essa linha [F, `scripts/component-docs.mjs`] |
| Recomendação por objetivo | `recommendationsByGoal` em `scripts/component-docs.mjs`: objetivo `table` com `{ component: 'ValueTable', reason: 'Lista de 3 a 6 itens com valor de unidade própria, texto ou nota.' }` | e uma asserção em `scripts/check-video-mcp.mjs` |
| Demos | `examples/charts/ValueTableDemo.tsx` (paisagem, 3 sequências de 110 quadros) e `ValueTableVerticalDemo.tsx` (1080×1920, 330 quadros), registradas em `examples/Root.tsx` na pasta `Charts` | **dados neutros** ("Empresa A", valores inventados; `AGENTS.md` do kit) |
| Quadros de documentação | entradas em `examples/stills.json` (início, meio e fim de cada demo) e `npm run docs:stills` | para `docs/stills/` |
| Testes | `src/charts/ValueTable.test.tsx` com `renderAtFrame` | seção 6 |
| Build | `npm run check` (typecheck, testes e bundle), build e `dist/` versionado | `AGENTS.md` do kit |
| Commit | `feat(charts): ValueTable, tabela de valores com entrada linha a linha` | Conventional Commits |

## 4. Camada B: a emenda às ADR 011 e 014 (texto proposto)

**ADR 011, emenda "tabela de valores":**

1. Novo tipo `table` (componente do kit: `ValueTable`; afirmação na tela: `claims` obrigatórias):
   - `title` (obrigatório), `header?` (`label`, `value`) e `rows` (de **2 a 6**: `label`, `value`, `note` padrão vazio, `anchor?`, `highlight` padrão `false` e `bar?`, o comprimento da barra).
   - `value` segue a regra do `number` e do `compare`: o texto como aparece na tela, por linha, sem conversão.
2. Regras de validação (erro em `scenes.json` e em `episode.json`): rótulos únicos; no máximo **uma** linha com `highlight`; `bar` em **todas** as linhas ou em nenhuma, e, com `bar`, todo `value` com **o mesmo prefixo e o mesmo sufixo** (como o `compare` em escala, que recusa unidades diferentes; só prefixo e sufixo são lidos do texto, **o número da barra é explícito**, ver a seção 7, item 6); com `anchor` em uma linha, **todas** têm, em ordem na narração, depois da âncora do plano (como `network.steps[].anchor`).
3. **Afirmações na tela:** `claims` do plano (herdadas de `_FactualShot`, no mínimo uma). **Não** repetir o padrão de `claims` por aresta da rede: hoje `check.py`, `shots.py` e `unknown_source_refs` percorrem só `scene.claims` e `shot.claims`, então as `claims` das arestas **não passam** pela checagem de trechos e fontes [F, lido no código; não testei com um caso real]. O agente `verificador` confere cada linha (`label` e `value`) contra os trechos citados. Quando houver `bar`, também a unidade comum e que cada `bar` bate com o `value` da linha (o contrato não tem como saber).
4. `episode.json`: `steps_ms` deixa de ser "só `network`": passa a valer também para `table` **com `anchor`** (um tempo por linha, relativo ao início do plano, calculado como o dos passos da rede: posição da âncora sobre a duração real do WAV, `app/pipeline/shots.py`). **Mudar o `episode.json` exige esta ADR** (`CLAUDE.md` §6).
5. Sem mudança no contrato: o template converte `steps_ms` em `stepFrames` (`app/render/remotion.py`, `_editorial`), como já faz com a rede.

**ADR 014, emenda:** `table` entra em `PORTRAIT_SHOT_KINDS` (de 8 para 9 planos em retrato), com o arranjo da seção 5.

## 5. Camada C: contrato, `vp check`, adaptador e template

### 5.1 Schema (`app/pipeline/schemas.py`)

```python
TABLE_MAX_ROWS = 6

class TableRow(Model):
    label: NonEmpty   # o que o valor mede, como aparece na tela
    value: NonEmpty   # texto como aparece na tela: "R$ 82,05", "6,5%", "último dia de maio"
    note: str = ""    # nota curta sob o rótulo
    anchor: NonEmpty | None = None  # trecho da narração em que a linha entra
    highlight: bool = False
    bar: float | None = None  # comprimento da barra, em escala comum a todas as linhas; só geometria

class TableHeader(Model):
    label: NonEmpty
    value: NonEmpty

class TableShot(_FactualShot):
    kind: Literal["table"] = "table"
    title: NonEmpty
    header: TableHeader | None = None
    rows: list[TableRow] = Field(min_length=2, max_length=TABLE_MAX_ROWS)
    # validadores: rótulos únicos; no máximo um `highlight`; âncoras todas ou nenhuma;
    # `bar` em todas as linhas ou em nenhuma, e então o mesmo prefixo e sufixo em todo `value`
```

`Shot` ganha `| TableShot`; `PORTRAIT_SHOT_KINDS` e `GRAPHIC_SHOT_KINDS` ganham `"table"` (não entra em `OVERLAY_SHOT_KINDS`: é tela cheia, como o `chart`). `EpisodeShot._steps_match` espera `len(rows)` tempos quando o plano é `table` com âncoras, `len(steps)` para a rede e zero nos outros. `step_positions` passa a aceitar os dois planos. O espelho em `video/src/types.ts` ganha `TableSpec`.

### 5.2 `vp check` (`app/pipeline/check.py`, `text_fit.py`)

| Regra | Valor proposto | Base |
|---|---|---|
| Tempo de leitura | `table` em `READING_KINDS` (mínimo de 4 s, como o `chart`) | [F] `READING_MS = 4000` |
| Teto de duração | `table` em `LONG_KINDS` quando as linhas têm âncora (a tabela dura enquanto a narração enumera as linhas) | [H] `MAX_SHOT_MS = 6000` não cabe em 6 linhas faladas |
| Rótulo | `TABLE_LABEL = (30, 2)` (caracteres por linha, linhas) | [I] coluna de ~560 px, letra 36, ≈0,5 de largura média |
| Valor | `TABLE_VALUE = (15, 1)` | [I] coluna de ~360 px, letra 44 em negrito, ≈0,55 |
| Nota | `TABLE_NOTE = (42, 1)` | [I] mesma coluna do rótulo, letra 26 |
| Variedade | o `table` conta como plano gráfico: `MAX_GRAPHIC_RUN` (4 seguidos sem imagem) e "o mesmo tipo duas vezes" já valem | [F] `variety_warnings` |
| Uma só unidade e 2 linhas | `chart` com 2 pontos já alerta "use `compare`"; **uma `table` de 2 linhas** com mesma unidade alerta "use `compare`" | [I] |

Os limites da tabela são estimativa (a mesma do `text_fit.py`: "WWW" ocupa mais que "iii") e **precisam ser conferidos em quadros** antes de virarem regra.

### 5.3 Adaptador (`app/render/remotion.py`)

`_editorial()` passa a emitir, para `table`, `stepFrames` (de `steps_ms`). O número de cada barra vai no próprio `bar` da linha: **nem o Python nem o TypeScript derivam o número do texto** (por quê: o aviso de idioma da seção 7, item 6).

### 5.4 Template (`video/src/Editorial.tsx`, `ShotView.tsx`, `types.ts`)

`TableShot` segue o `ChartShot` [F]: mesmo contêiner, com `Title` (o título do plano) e a tabela abaixo. Em retrato: `width={kit(940)}`, `labelSize={kit(36)}`, `valueSize={kit(44)}`, `noteSize={kit(26)}`, linhas a partir de `safe.top + 150` e acima de `safe.bottom + 280`, **no máximo ≈560 px de altura útil** (o que limita a 5 linhas com nota ou 6 sem) [I, conta sobre o `ChartShot`]. Em paisagem: `width={1200}` e os defaults do kit. `enter="rise"` (a régua não muda); `rowFrames={stepFrames}` quando existir; sem `stepFrames`, `at={6}` e `stagger` padrão. A fonte do rodapé vem das `claims`, como nos outros planos [F, `shots.py`].

**Apresentador (`app/media/host.py`, `blocked_corners`):** em retrato, `table` **bloqueia os dois cantos de cima** (o título e as linhas ocupam o topo) e, como o `chart`, **não conta como conteúdo centralizado**: numa cena só de gráficos, tabelas e réguas os cantos de baixo ficam livres. Em paisagem, bloqueia o canto de cima à esquerda (o título). Muda a regra, muda o teste de `host.py`. **Esta linha faltava na primeira versão da spec.**

### 5.5 Skills e docs que mudam

| Arquivo | Mudança |
|---|---|
| `.claude/skills/roteiro-explicativo/SKILL.md` | linha na tabela "A frase...": "lista 3 a 6 itens com valor de unidade própria, texto ou ressalva → `table`" |
| `.claude/skills/roteiro-explicativo/planos.md` | seção `table` com exemplo e a regra de quando usar (seção 1 desta spec) |
| `.claude/skills/checagem/SKILL.md` | conferir cada `label` e `value` contra o trecho; `bar` só com unidade comum e coerente com o `value`; nenhum total, razão ou variação na tabela |
| `docs/decisions/011` e `014` | as emendas da seção 4 |
| `CLAUDE.md` §6 | a lista de planos do perfil vertical passa a ter `table` |

## 6. Testes e aceite

**Kit (`src/charts/ValueTable.test.tsx`, `node:test`, `renderAtFrame`; padrão de `Pane.test.tsx` [F])**

1. Antes de `rowFrames[i]` a linha existe no HTML com `visibility:hidden` (o espaço fica reservado); no quadro dela e depois, visível.
2. `cut`: opacidade 1 no quadro de entrada; `rise`: parcial dois quadros depois; `pop`: escala menor que 1 no primeiro quadro e 1 ao fim de 4.
3. `highlight` aplica `theme.accent`; `highlightAt` atrasa a cor; as outras linhas ficam em `theme.text`.
4. Barras proporcionais ao maior; **uma linha sem `bar` ⇒ nenhuma barra**.
5. O valor tem `white-space:nowrap` e `font-variant-numeric:tabular-nums`.
6. O mesmo quadro devolve o mesmo HTML (determinismo).
7. Em 1080×1920 os tamanhos acompanham `useUnit` (como em `Pane.test.tsx`).
8. `at` negativo: todas as linhas já assentadas no quadro 0.

**Revisão visual (kit):** `npm run still` nos quadros de início, meio e fim de cada demo, em paisagem e em retrato, com o que foi visto e o que ficou pendente (`AGENTS.md` do kit: "renderização bem-sucedida não certifica qualidade visual").

**Contrato e template (`tests/`, padrão de `test_editorial_shots.py` [F])**

1. Plano válido nos três casos de aceite da seção 2 (com `claims`), em retrato e em paisagem.
2. Erros: menos de 2 ou mais de 6 linhas; rótulos repetidos; dois `highlight`; `bar` só em algumas linhas ou com unidades misturadas; âncoras fora de ordem ou só em algumas linhas; plano sem `claims`.
3. `episode.json`: `steps_ms` com um tempo por linha, em ordem e dentro do plano.
4. `portrait_problems`: `table` não é erro em retrato (e a mensagem lista os 9 planos).
5. `text_fit` e leitura: alertas de rótulo, valor e nota; `table` com menos de 4 s.

**Régua:** a folha de quadros do vídeo-régua **não deve mudar** (nenhum plano existente muda), com sonda de CPU antes. A tabela em si se revê num quadro parado de um episódio de teste; **render só com autorização do dono**.

## 7. Riscos e decisões abertas

| # | Questão | Para decidir |
|---|---|---|
| 1 | Tokens de movimento (`cut`/`pop`/`rise`) ainda não existem; escala inicial do `pop` | seguir o guia, seção 2; a `ValueTable` não espera a PR de tokens |
| 2 | **Onde ficam as `claims`**: no plano (recomendado, passam pelo `vp check`) ou por linha (como a rede, que hoje não passa) | dono, na ADR |
| 3 | Teto de 6 linhas e `LONG_KINDS` para `table` com âncora | dono, na ADR; medir no vídeo-régua |
| 4 | Limites de texto (`TABLE_LABEL`, `TABLE_VALUE`, `TABLE_NOTE`) são estimativa | conferir em quadros |
| 5 | Retrato com 6 linhas e nota estoura a altura útil (≈560 px) [I] | limite de linhas com nota, ou fonte menor |
| 6 | **Números em inglês estão quebrados no pipeline de hoje** [F, testado]: `screen_number` (Python) e `screenNumber` (TypeScript) leem só pt-BR (`.` é milhar e `,` é decimal): `"US$ 1,500"` vira 1,5, `"$4.2 bn"` vira 42 e `"15.3%"` vira 153. O `Odometer` do `NumberShot` está fixo com `decimalSeparator=","` e `groupSeparator="."`; o adaptador não leva o idioma do episódio ao template; `BarChart` fixa `pt-BR`. **A `ValueTable` não depende disso** (o `value` é texto pronto e a barra é numérica explícita), mas `number`, `compare` em escala e os gráficos numéricos, sim | **fora desta spec e bloqueia as verticais em inglês**; ver `docs/pesquisa/nichos-globais-2026-10.md`, nota de 2026-10-07 |
| 7 | **`claims` por aresta da rede não passam pelo `vp check`** [F, leitura do código] | **fora desta spec**; vale uma PR própria (e um teste) |
| 8 | Preset claro ou segunda identidade | a `ValueTable` só usa tokens do tema e não precisa mudar |
| 9 | Esforço: camada A ≈ médio; B, só texto; C ≈ médio a grande | [I] estimativa relativa, sem dias |

## 8. Ordem de entrega

1. **PR do kit** (camada A), com demos e testes. Mostrar os quadros antes do merge.
2. **PR de docs** (camada B): as emendas às ADR 011 e 014, para o dono decidir os itens 2 e 3 da seção 7.
3. **PR do template e do contrato** (camada C): schema, `vp check`, `text_fit`, adaptador, template, skills, testes e pin novo do kit (`CLAUDE.md` §14: cruzar o SHA do pin com o checkout). Vídeo-régua e sonda de CPU.
