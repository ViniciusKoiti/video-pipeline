# Spec: `RevealList` (motion-kit) e o plano `list` (template e contrato)

- **Estado:** rascunho para aprovação do dono (2026-10-07). **Nada aqui está implementado.** Onde diz **decisão aberta**, o agente não decide: pergunta ao dono. Em conflito valem `CLAUDE.md`, as ADRs e o `AGENTS.md` do kit.
- **Origem:** item 3 de `docs/pesquisa/componentes-infografico-2026-10.md` e a seção 5 de `docs/guia-animacao-de-texto.md` (a lista que acumula do Reel de referência).
- **Irmã da `ValueTable` e do `LimitMeter`** (`docs/specs/value-table.md`, `docs/specs/limit-meter.md`): **o que é igual (as três camadas, os entregáveis do kit, a emenda conjunta às ADR 011 e 014, a regra de cantos do apresentador, o aviso de idioma) não se repete aqui**; esta spec registra as diferenças.
- **Rótulos:** [F] confirmado em arquivo; [I] inferência; [H] hipótese a medir.
- **Três camadas, três PRs:** **A** o componente no kit (em `editorial/`, não em `charts/`: é texto, não dado); **B** a emenda às ADR 011 e 014 (a mesma da `table` e do `limit`); **C** o plano `list` no contrato, no `vp check`, no adaptador e no template.

## 1. O que é, e o que não é

**É** uma lista numerada (ou com marcador) que **cresce no ritmo da narração**: cada item entra quando é dito e fica. É o mecanismo do Reel de referência (título e 5 itens, cada um num quadro só, acumulando por 25 s) [F, `docs/pesquisa/animacao-reel-referencia-2026-10.md`].

**Por que existe [F]:** hoje a única forma de enumerar é repetir o plano `keyword`, e o `vp check` **alerta** para mais de um `keyword` por cena (`check.py` l. 245 e 246); o `keyword` mostra **uma** frase por vez, e a lista é uma **estrutura que acumula**. O `YearTimeline` e a rede não servem: a linha do tempo está fora do retrato (ADR 014) e a rede é de relações.

**Não é:** uma tabela (**sem valores**: se cada item tem um valor de unidade própria, é `table`), uma sequência de `keyword` (cada item é parte de um todo que o espectador vê crescer) nem texto livre: **cada item é cópia literal da narração**, como o `keyword` (seção 4). A lista não acrescenta nada à tela que a narração já não diga.

**Quando usar [I]:** enumera **passos, partes ou categorias** (preço em quatro partes, quem pode representar você, passo a passo) → `list`; cada item com **valor** → `table`; uma frase só → `keyword`.

## 2. Casos de aceite (dados reais, só no template; o kit usa dados neutros)

| # | Título (literal da narração) | Itens (literais, na ordem em que a narração os diz) | Fonte |
|---|---|---|---|
| 1 | "O preço tem quatro partes" | custos fixos; custos variáveis; imposto; margem de lucro | método do Sebrae/MS (fonte única, a marcar; `nichos-reels-animados.md` §7.3, formato M3) |
| 2 | "Quem pode representar você no USCIS" | advogado; advogado estrangeiro; representante credenciado; estudante de Direito supervisionado | página do USCIS (`nichos-globais-anexos/imigracao-ficha.md`; as 4 categorias vêm de resumo do leitor: **conferir na página**) |
| 3 | (sem título) | seis itens neutros, de 1 linha, e depois quatro itens de 2 linhas | caso de capacidade da seção 5.2 |

Narração do caso 1 [I, exemplo]: "O preço tem quatro partes: custos fixos, custos variáveis, imposto e margem de lucro." O título é o trecho "O preço tem quatro partes" e cada item, um trecho **exato** da narração (`custos fixos`, `custos variáveis`, `imposto`, `margem de lucro`), na ordem em que ela os diz.

## 3. Camada A: o componente no kit

**Onde:** `src/editorial/RevealList.tsx` (peças sóbrias, ao lado de `KineticHeadline` e `Highlighter` [F]), exportado em `src/editorial/index.ts` com `RevealList`, `RevealListProps` e a função pura `revealListLayout`. Entregáveis iguais aos da `ValueTable` (§3.3 daquela spec): linha em `src/COMPONENTS.md` (módulo editorial), objetivo `list` em `recommendationsByGoal` (`scripts/component-docs.mjs`) e asserção em `scripts/check-video-mcp.mjs`, demos em `examples/editorial/RevealListDemo.tsx` (paisagem) e uma vertical (1080×1920), com **dados neutros**, quadros em `examples/stills.json`, `npm run check`, build e `dist/`.

### 3.1 API

```ts
export interface RevealListProps {
  /** Os itens, como aparecem na tela. O kit não os edita nem os numera por conta própria além do marcador. */
  items: string[];
  /** Título acima da lista. Opcional. Entra em `at`. */
  title?: string;
  /** Marcador: `'number'` (1., 2., ...), `'dot'` ou `'none'`. Default: `'number'`. */
  marker?: 'number' | 'dot' | 'none';
  /** Frame em que o título entra (ou o primeiro item, sem título). Default: 0. Negativo: já assentado. */
  at?: number;
  /** Frames entre itens quando `itemFrames` não vem. Default: 24. */
  stagger?: number;
  /** Frame de entrada de CADA item (relativo à peça), na ordem, para casar com a narração; substitui
   *  `at` + `stagger`. Negativo: o item já está na tela, assentado, sem animação (como a janela do
   *  apresentador, `at={-60}`). */
  itemFrames?: number[];
  /** Entrada do título e de cada item: `'cut'`, `'pop'` ou `'rise'`. Default: `'rise'`. */
  enter?: 'cut' | 'pop' | 'rise';
  /** Quando um item novo entra, os anteriores passam para `theme.muted`. Default: `false`. */
  dimPrevious?: boolean;
  /** Largura do bloco, em px de um quadro de 1080 de altura. Default: 1200. */
  width?: number;
  /** Tamanhos, em px de um quadro de 1080 de altura. Defaults: 48 (itens) e 40 (título). */
  itemSize?: number;
  titleSize?: number;
  /** Frame em que tudo sai (10 quadros). Sem ele, fica até o fim. */
  exitAt?: number;
  style?: CSSProperties;
}
```

Nomes que repetem o kit [F]: `at`, `stagger` e `itemFrames` espelham `KineticHeadline` (`at`, `stagger`, `wordFrames`), a `ValueTable` (`rowFrames`) e o `LimitMeter` (`tickFrames`); o `at` negativo espelha `at={-60}` de `HostWindow.tsx`.

### 3.2 Comportamento e layout

- **Ancoragem à esquerda.** Título (em `theme.muted`, negrito) e itens alinhados à esquerda, em coluna: numeral ou marcador numa coluna fixa (largura do maior numeral, medida por `labelWidth` de `charts/scale.ts` [F]) e o texto ao lado, com até 2 linhas, indentação pendente (a segunda linha começa sob a primeira, não sob o numeral).
- **Espaço reservado.** A altura total sai de `revealListLayout` (função pura, testada à parte, como `splitLayout` e `floatingMotion` [F]): **todos os itens têm o lugar desde o primeiro quadro** (os que ainda não entraram ficam com `visibility: hidden`), então os itens já na tela **não se mexem** quando outro chega. O bloco cresce para baixo a partir do título.
- **Entrada.** `rise` (14 quadros, 24 px, ease-out cúbico, os valores de `useInOut` e `useAnimateIn` [F]), `cut` (num quadro; **é o que a referência faz**) e `pop` (4 quadros; escala inicial é **decisão aberta**, 0,85 provisório). **Sem mola em linha**: usa o mesmo auxiliar de entrada da `ValueTable`, que depois lê os tokens do guia.
- **Item atual.** O item que acabou de entrar tem o **numeral em `theme.accent`** e o texto com peso maior; quando o próximo chega, o anterior volta ao normal numa **troca seca**. Com `dimPrevious`, os anteriores também ficam em `theme.muted` (**decisão aberta do padrão**: `false` espelha a referência, em que todos ficam legíveis; `true` direciona o olhar, no estilo do `Focus` e do `Highlighter`).
- **Tema.** Só `useMotionTheme()` (`text`, `muted`, `accent`, `font`) e `withAlpha`; **nenhuma cor escrita no componente**.
- **Determinismo e custo.** Só `useCurrentFrame`; sem `Math.random`, sem filtro, sem `blur` e sem sombra difusa [I].
- **Bordas.** Zero itens: não desenha. Um item: desenha (o contrato exige 2). `itemFrames` menor que `items`: o resto segue o `stagger`. `at` negativo: tudo assentado. Item que quebra em 3 linhas ou mais: o bloco cresce e o alerta vem do `vp check` (seção 5.2); **falha visível é melhor que texto cortado**.
- **Fora de escopo da v1:** destaque de palavras dentro do item (isso é o `KineticHeadline`), ícone por item, sublista, rolagem, item que sai, visual de painel de partidas.

### 3.3 O que a lista **não** resolve sozinha

- **Cada cena é um render [F].** Uma lista **não atravessa** o corte entre cenas. Para continuar a mesma lista na cena seguinte, repete-se a lista com os itens anteriores em `itemFrames` negativos (assentados), como a janela do apresentador. O roteirista planeja uma lista por cena (uma cena tem de 5 a 12 s e de 1 a 3 frases [F, skill `roteiro-explicativo`]).
- **O tempo por item é o da narração.** O ritmo irregular da referência (2,6 a 6,7 s entre itens, medida de um revisor) não cabe no `useStagger` (uniforme); por isso o `itemFrames` explícito.

## 4. Camada B: a emenda às ADR 011 e 014 (texto proposto)

**Uma só emenda, junto com a `table` e o `limit`** ("infográficos em retrato"); o texto de `table` está em `value-table.md` §4 e o de `limit`, em `limit-meter.md` §4. Para o `list`:

1. Novo tipo `list` (componente do kit: `RevealList`; **sem `claims` próprias**, como o `keyword`):
   - `title?` (opcional); `items` (de **2 a 6**: `text` e `anchor?`); `marker` (`number` | `dot` | `none`, padrão `number`).
2. **Cada `text` (e o `title`) é cópia literal da narração da cena**, sem diferença de maiúscula nem de espaços, **como o `keyword`** (`Scene._visual_plan`: `_fold(text) in _fold(narração)` [F]). Por isso o plano **não repete `claims`**: o que aparece na tela já está na narração, que tem as suas.
3. **`anchor` do item** (trecho **exato** da narração em que ele entra; padrão: o próprio `text`, que então tem de aparecer **exatamente** assim): em ordem, depois da âncora do plano e dentro do trecho dele, como `network.steps[].anchor` (`step_positions` [F]). O `anchor` serve para o item `Custos fixos` entrar quando a narração diz "custos fixos". O roteirista escreve a narração com os rótulos dos itens, como já faz com o `keyword`.
4. Regras de validação (erro em `scenes.json` e em `episode.json`): de 2 a 6 itens; cada item com **no máximo 8 palavras** (`KEYWORD_MAX_WORDS`); itens únicos (comparação sem maiúscula nem espaços); `title` com no máximo 8 palavras e, se existir, dito **antes** do primeiro item.
5. `episode.json`: `steps_ms` passa a valer também para `list`, **sempre** (como o plano não tem item sem tempo, `len(items)` tempos, relativos ao início do plano, calculados como os da rede). **Mudar o `episode.json` exige esta ADR** (`CLAUDE.md` §6).
6. **Legenda (decisão aberta):** a ADR 011 (decisão 5) esconde a legenda enquanto um `keyword` está na tela, porque a mesma frase duas vezes confunde. A lista **não** esconde a legenda por padrão: ela é uma estrutura que acumula e a legenda continua dizendo a frase inteira (na referência, as duas convivem). Se o dono preferir esconder, é um acréscimo em `Scene.tsx` (`list` entra na condição do `keyword`).

**ADR 014, emenda:** `list` entra em `PORTRAIT_SHOT_KINDS` (com `table` e `limit`: de 8 para 11 planos em retrato).

## 5. Camada C: contrato, `vp check`, adaptador e template

### 5.1 Schema (`app/pipeline/schemas.py`)

```python
LIST_MAX_ITEMS = 6
LIST_ITEM_MAX_WORDS = KEYWORD_MAX_WORDS  # 8

class ListItem(Model):
    text: NonEmpty                  # cópia literal da narração (sem diferença de maiúscula nem de espaços)
    anchor: NonEmpty | None = None  # trecho EXATO da narração em que o item entra; sem ele, vale o `text`

class ListShot(_Shot):
    kind: Literal["list"] = "list"
    title: str = ""                 # opcional; cópia literal da narração
    items: list[ListItem] = Field(min_length=2, max_length=LIST_MAX_ITEMS)
    marker: Literal["number", "dot", "none"] = "number"
    # validadores: itens únicos; até 8 palavras por item e por título
```

`Scene._visual_plan` ganha o ramo de `ListShot` ao lado do de `KeywordShot` (`text` e `title` literais na narração) e do de `NetworkShot` (`step_positions`, generalizado para os itens). `Shot` ganha `| ListShot`; `PORTRAIT_SHOT_KINDS` e `GRAPHIC_SHOT_KINDS` ganham `"list"` (tela cheia, como o `chart`; fora de `OVERLAY_SHOT_KINDS`). `EpisodeShot._steps_match` espera `len(items)` tempos para `list`. O espelho em `video/src/types.ts` ganha `ListSpec`.

### 5.2 `vp check` (`app/pipeline/check.py`, `text_fit.py`)

| Regra | Valor proposto | Base |
|---|---|---|
| Teto de duração | `list` em `LONG_KINDS` (a lista dura enquanto a narração enumera os itens) | [F] `MAX_SHOT_MS = 6000` não cabe em 4 a 6 itens falados |
| Tempo entre itens | **alerta** quando dois itens entram com menos de **1,5 s** de diferença (`LIST_MIN_STEP_MS = 1500`; é o `MIN_SHOT_MS`) | [F] `MIN_SHOT_MS = 1500`; [I] a posição de cada item sai do modelo de tempo proporcional, com o erro de ~0,8 s que a ADR 015 registrou |
| Item | `LIST_ITEM = (38, 2)` (caracteres por linha, linhas) | [I] **medido em retrato, o mais estreito** (a paisagem comporta mais): coluna de ~870 px, letra 44 (≈0,5 de largura média = 22 px por caractere → 39; usar 38) |
| Título | `LIST_TITLE = (40, 1)` | [I] retrato: 940 px, letra 40 em negrito (≈0,55 = 22 px por caractere → 42; usar 40) |
| Altura | no máximo **8 linhas somadas** (título mais itens) em retrato | [I] ≈560 px úteis; linha de 48 px × 1,25 = 60, mais espaço entre itens |
| Uma lista por cena | duas listas na mesma cena: alerta, como o de mais de um `keyword` | [F] `check.py` l. 245 |
| Variedade | conta como plano gráfico: `MAX_GRAPHIC_RUN` e "o mesmo tipo duas vezes" já valem | [F] `variety_warnings` |

Os limites são estimativa (a mesma de `text_fit.py`) e **precisam ser conferidos em quadros**; o caso 3 (capacidade) é o teste.

### 5.3 Adaptador e template

- **Adaptador (`app/render/remotion.py`, `_editorial`):** `list` emite `stepFrames` (um por item), como a rede.
- **Template (`video/src/Editorial.tsx`, `ShotView.tsx`, `types.ts`):** `ListShot` segue o `ChartShot` [F]: mesmo contêiner (a partir de `safe.top + 150`, acima de `safe.bottom + 280`), alinhado ao topo, **sem `Title` externo** (o título é o da lista, para não aparecer duas vezes). Em retrato: `width={kit(940)}`, `itemSize={kit(44)}`, `titleSize={kit(40)}`; em paisagem, os defaults do kit, com `width={1200}` e a coluna alinhada à esquerda das margens de 160 px. `enter="rise"` (a régua não muda; `cut` quando o dono decidir pelo estilo da referência); `itemFrames={stepFrames}`. **Sem fonte no rodapé**: o plano não tem `claims` (como o `keyword`).
- **Apresentador (`app/media/host.py`, `blocked_corners`):** em retrato, `list` **bloqueia os dois cantos de cima** (a lista ocupa o topo) e, como o `chart`, **não conta como conteúdo centralizado**. Em paisagem, bloqueia o canto de cima à esquerda (onde a lista começa). Muda a regra, muda o teste de `host.py`.
- **Skills e docs:** `roteiro-explicativo/SKILL.md` ("a frase enumera passos, partes ou categorias → `list`: escreva a narração com o rótulo de cada item, até 8 palavras; no máximo 6 itens; uma lista por cena") e `planos.md` (seção `list`, com os casos 1 e 2); `checagem/SKILL.md` (cada item e o título são **literais**; a ordem é a da narração; nenhum item acrescenta fato; nenhum número na lista que não esteja na narração); `docs/guia-animacao-de-texto.md` §5 (a lista deixa de ser "fora do primeiro conjunto" quando esta spec for aprovada); `CLAUDE.md` §6 (lista de planos do retrato).

## 6. Testes e aceite

**Kit (`src/editorial/RevealList.test.ts(x)`, `node:test`; `renderAtFrame` como em `Pane.test.tsx` [F])**

1. `revealListLayout`: altura total e posição de cada item; item de 2 linhas desloca os seguintes; numeral de maior largura define a coluna; **a altura não muda com o número de itens já entrados** (espaço reservado).
2. Antes de `itemFrames[i]` o item existe no HTML com `visibility:hidden`; no quadro dele e depois, visível; `cut` entra com opacidade 1 no quadro; `rise`, parcial dois quadros depois.
3. Item atual: numeral em `theme.accent` só no último entrado; o anterior volta ao normal no quadro em que o próximo entra; com `dimPrevious`, os anteriores usam `theme.muted`.
4. `itemFrames` negativo: o item está assentado no quadro 0, sem animação; `at` negativo: tudo assentado.
5. Com um tema de cores trocadas, a saída usa **só** as cores do tema.
6. Determinismo e tamanhos em 1080×1920 por `useUnit`; `marker: 'none'` e `'dot'` não reservam a coluna do numeral.

**Revisão visual (kit):** `npm run still` em início, meio e fim de cada demo, em paisagem e em retrato, com **a lista de 6 itens de 1 linha** e **a de 4 itens de 2 linhas** à vista.

**Contrato e template (`tests/`, padrão de `test_editorial_shots.py` [F])**

1. Planos válidos nos casos 1 e 2, com a narração que contém os itens, em retrato e em paisagem.
2. Erros: item que não está na narração; itens fora de ordem; `anchor` que não aparece na ordem; menos de 2 ou mais de 6 itens; item com mais de 8 palavras; título dito depois do primeiro item; itens repetidos.
3. `episode.json`: `steps_ms` com um tempo por item, em ordem e dentro do plano.
4. `portrait_problems` aceita `list`; `text_fit` (item, título, altura); alerta de itens a menos de 1,5 s; `host.py` (cantos de cima bloqueados em retrato, bloqueio de canto superior esquerdo em paisagem).

**Régua:** a folha de quadros do vídeo-régua **não deve mudar** (nenhum plano existente muda), com sonda de CPU antes. O visual da lista se revê num quadro parado; **render só com autorização do dono**.

## 7. Riscos e decisões abertas

| # | Questão | Para decidir |
|---|---|---|
| 1 | **Item literal da narração**: obriga a escrever a narração com os rótulos (como o `keyword`); é a defesa contra texto na tela que a narração não disse | dono, na ADR; alternativa: `claims` por item, como a `table` |
| 2 | Padrão de `dimPrevious` (`false`, como a referência, ou `true`) e de `enter` (`rise` ou `cut`) | dono, junto com a segunda identidade e os tokens |
| 3 | A legenda continua na tela com a lista (seção 4, item 6) | dono, na ADR |
| 4 | O tempo de entrada de cada item sai do **modelo proporcional** (erro de ~0,8 s, ADR 015) | itens entram fora de hora até haver alinhamento (#17); `cut` expõe o erro mais que `rise` [I] |
| 5 | Lista de itens longos (2 linhas) estoura a altura útil (≈560 px) [I] | limite de 8 linhas; conferir no caso 3 |
| 6 | Lista **não atravessa** o corte de cena | seção 3.3; um plano `list` por cena |
| 7 | Em retrato, a lista no topo disputa lugar com a janela do apresentador | regra de `host.py` (cantos de cima bloqueados); cena só de gráficos libera os de baixo |
| 8 | Limites de texto (`LIST_ITEM`, `LIST_TITLE`) são estimativa | conferir em quadros |
| 9 | Esforço: kit ≈ médio; B, só texto; C ≈ médio | [I] estimativa relativa, sem dias |

## 8. Ordem de entrega

1. **PR do kit** (camada A): componente, `revealListLayout`, demos e testes; pode andar **em paralelo** com as da `ValueTable` e do `LimitMeter`. Mostrar os quadros antes do merge.
2. **PR de docs** (camada B): **uma emenda** às ADR 011 e 014 para `table`, `limit` e `list`, e a decisão dos itens abertos.
3. **PR do template e do contrato** (camada C), com o pin novo do kit, o vídeo-régua e a sonda de CPU; as skills e o guia atualizados no mesmo PR.
