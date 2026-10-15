# Spec: `LimitMeter` (motion-kit) e o plano `limit` (template e contrato)

- **Estado:** rascunho para aprovação do dono (2026-10-07). **Nada aqui está implementado.** Onde diz **decisão aberta**, o agente não decide: pergunta ao dono. Em conflito valem `CLAUDE.md`, as ADRs e o `AGENTS.md` do kit.
- **Origem:** item 2 de `docs/pesquisa/componentes-infografico-2026-10.md`. É a irmã da `ValueTable` (`docs/specs/value-table.md`): **o que é igual (as três camadas, os entregáveis do kit, a regra das `claims` no plano, a generalização de `steps_ms`) não se repete aqui; vale o que aquela spec diz**, e esta só registra as diferenças.
- **Rótulos:** [F] confirmado em arquivo; [I] inferência; [H] hipótese a medir.
- **Três camadas, três PRs:** **A** o componente no kit; **B** a emenda às ADR 011 e 014 (a mesma da `ValueTable`, num texto só); **C** o plano `limit` no contrato, no `vp check`, no adaptador e no template.

## 1. O que é, e o que não é

**É** uma régua linear com **marcos** (os limites, cada um com o valor e o nome), **faixas** entre eles (o que acontece de cada lado) e, opcionalmente, **um marcador** com um valor que vem de uma ficha. Serve a uma frase como "o limite é R$ 81 mil; até 20% acima paga-se DAS complementar".

**Por que existe [F]:** nenhum plano do retrato mostra **onde um valor cai em relação a um limite**. O `chart` desenha barras e linhas de uma série; o `compare` tem dois lados; o `Gauge` do kit é radial, em neon, de agulha na zona vermelha ("a dor de hook analógica") e **não tem plano**. Os formatos mapeados pedem uma régua sóbria: o "termômetro do limite" do MEI (`nichos-reels-animados.md` §6.A, formato 4), o limite de açúcar por refeição, o piso do imposto do autônomo.

**Não é:** gráfico de série, medidor radial, nem calculadora. **A tela não calcula (ADR 011, decisão 7):** nada de "faltam R$ X para o limite", percentual do limite ou margem restante. O kit mostra o texto que recebe; a posição na régua é só geometria.

**Quando usar [I]:** uma grandeza **e** os limites dela → `limit`; **várias grandezas** de unidades diferentes (por exemplo, US$ 20.000 **e** 200 transações do 1099-K) → `table`, não duas réguas; dois valores a comparar → `compare`; série no tempo → `chart` com `line`.

## 2. Casos de aceite (dados reais, só no template; o kit usa dados neutros)

| # | Título | Marcos (`valor` → `rótulo`) | Faixas, da menor para a maior | Fonte |
|---|---|---|---|---|
| 1 | Limite de faturamento do MEI | R$ 81 mil → "Limite anual"; R$ 97.200 → "Limite com 20% de tolerância" | "Dentro do limite" (base); "DAS complementar e ME no ano seguinte" (destaque); **sem texto** acima de R$ 97.200 (a ficha não diz o que acontece) | gov.br/memp, modificado em 2026-09-16 (`nichos-reels-animados.md` §6.A) |
| 2 | Imposto do autônomo nos EUA | US$ 400 → "Ganho líquido do autônomo" | sem texto abaixo; "Imposto do autônomo se aplica" (destaque) | IRS, página lida em 2026-10-07 (`nichos-globais-anexos/freelance-ficha.md`) |
| 3 | Açúcar adicionado por refeição | 10 g → "Máximo por refeição" | "Dentro da diretriz" (base); "Acima da diretriz" (destaque) | Diretrizes Alimentares dos EUA 2025 a 2030, p. 4 (`nichos-globais-anexos/nutricao-ficha.md`) |

**Geometria do caso 1 [I, conta minha]:** em 940 px de régua e escala de 0 a 116.640 (o último marco × 1,2), os marcos caem em x ≈ 653 e x ≈ 783, **130 px de distância**, com blocos de ~200 a 260 px: eles **se sobrepõem** e o `placeLabels` tem de afastá-los (seção 3.2). É o caso que prova o layout.

O **marcador** só entra com valor de uma ficha (**decisão aberta:** exemplo hipotético, como "um MEI que faturou R$ 90 mil", exige uma ADR própria; ver `nichos-reels-animados.md` §2.5, item 2). Nenhum caso de aceite o usa; ele é testado com dados neutros.

## 3. Camada A: o componente no kit

**Onde:** `src/charts/LimitMeter.tsx`, exportado em `src/charts/index.ts` com `LimitMeter`, `LimitMeterProps`, `LimitTick`, `LimitBand`, `LimitMarker` e a função pura `limitMeterLayout`. Mesmos entregáveis, comandos e convenções da `ValueTable` (§3.3 daquela spec): catálogo em `COMPONENTS.md`, objetivo `limit` em `recommendationsByGoal` (`scripts/component-docs.mjs`) e asserção em `scripts/check-video-mcp.mjs`, demos com **dados neutros** em `examples/charts/`, quadros em `examples/stills.json`, `npm run check`, build e `dist/`.

### 3.1 API

```ts
export interface LimitTick {
  /** Posição na escala. Só geometria: o kit não a mostra nem a formata. */
  at: number;
  /** Valor como aparece na tela, texto pronto ("R$ 81 mil"). O kit não formata, não traduz nem converte. */
  value: string;
  /** O que o limite é ("Limite anual"). */
  label: string;
}

export interface LimitBand {
  /** Texto curto sob a faixa. Opcional. */
  label?: string;
  /** `'base'` (neutra) ou `'emphasis'` (cor de destaque do tema, com hachura). Default: `'base'`. */
  tone?: 'base' | 'emphasis';
}

export interface LimitMarker {
  /** Posição na escala (geometria). */
  at: number;
  /** Valor como aparece na tela. Tem de vir de uma ficha. */
  value: string;
  label: string;
}

export interface LimitMeterProps {
  /** De 1 a 3 marcos, em ordem crescente de `at`. */
  ticks: LimitTick[];
  /** Zero ou `ticks.length + 1` faixas, da menor para a maior. Sem elas, tudo é `'base'` e sem texto. */
  bands?: LimitBand[];
  marker?: LimitMarker;
  /** Início da escala. Default: 0. */
  min?: number;
  /** Fim da escala. Default: o último marco + 20% da distância desde `min` (só margem; **não aparece**). */
  max?: number;
  /** Frame em que a régua começa. Default: 0. */
  at?: number;
  /** Frames entre marcos quando `tickFrames` não vem. Default: 14. */
  stagger?: number;
  /** Frame de entrada de CADA marco, na ordem, para casar com a narração; substitui `at` + `stagger`. */
  tickFrames?: number[];
  /** Frame de entrada do marcador. Default: o último marco + `stagger`. */
  markerFrame?: number;
  /** Entrada: `'cut'`, `'pop'` ou `'rise'`. Default: `'rise'`. */
  enter?: 'cut' | 'pop' | 'rise';
  /** Largura da régua, em px de um quadro de 1080 de altura. Default: 1200. */
  width?: number;
  /** Tamanhos, em px de um quadro de 1080 de altura. Defaults: 40, 26 e 28. */
  valueSize?: number;
  labelSize?: number;
  trackHeight?: number;
  /** Frame em que tudo sai (10 quadros). */
  exitAt?: number;
  style?: CSSProperties;
}
```

Nomes que repetem o kit [F]: `at`, `stagger` e `tickFrames` espelham `KineticHeadline` e a `ValueTable`; `tone` e a lista de faixas lembram o `GaugeZone` (`upTo`, `color`), mas as faixas daqui **nascem dos marcos**: não há valor absoluto para duplicar nem faixa que fure ou sobreponha outra.

### 3.2 Comportamento e layout

- **Posição.** `x(v) = (v - min) / (max - min) × width`, linear; escala logarítmica fora de escopo. Valor fora de `[min, max]` é **limitado às pontas** (o contrato já recusa).
- **Régua.** Barra de `trackHeight` (28), cantos de 4 px. Faixa `base`: `withAlpha(theme.muted, 0.35)`. Faixa `emphasis`: `theme.accent` com **hachura diagonal** (`<pattern>` SVG de 6 px; **não é filtro**) para que a diferença **não dependa só da cor** [I].
- **Marcos.** Um traço de 4 px que cruza a régua. Em cima, o bloco do marco: o `value` em negrito (40) e o `label` em `theme.muted` (26, até 2 linhas). Os blocos são posicionados com `placeLabels(anchors, widths, gap, min, max)` de `charts/scale.ts` [F], com a largura medida por `labelWidth` (`measureText`, determinístico); o limite de cada bloco é 280 px. Quando um bloco sai do seu marco, uma linha-guia fina o liga de volta.
- **Faixas.** O `label` da faixa vai **sob a régua**, centrado na faixa, também por `placeLabels`, com até 2 linhas e uma chave fina marcando o trecho que a faixa cobre.
- **Marcador.** Triângulo apontando para a régua e, numa linha própria abaixo dos textos das faixas, o `value` e o `label`. Por isso nunca disputa lugar com o texto de uma faixa.
- **Altura total** calculada de `valueSize`, `labelSize` e do número de linhas (medido), sem depender de CSS. Em retrato, com marcos de 2 linhas e marcador, fica em ~340 px [I, conta minha], dentro dos ≈560 px úteis do `ChartShot` [F].
- **Entrada.** A régua entra em `at` (neutra, de ponta a ponta). **O marco `i` entra em `tickFrames[i]`** e, junto com ele, **a faixa à sua esquerda** se preenche (cresce da borda esquerda da faixa até o marco; com `cut`, num quadro); a última faixa (à direita do último marco) se preenche com o último marco. O marcador entra por último, com `pop`. `rise`, `cut` e `pop` seguem a `ValueTable` (§3.2 daquela spec: 14 quadros, 0 e 4; escala inicial do `pop` é **decisão aberta**, 0,85 provisório).
- **Tema.** Só `useMotionTheme()` (`text`, `muted`, `accent`, `line`, `font`) e `withAlpha`; **nenhuma cor escrita no componente**. O editorial só tem **um** destaque (dourado) e nenhum "vermelho de alerta": `emphasis` é "a faixa que a narração comenta", não "perigo". Um token de alerta, se um tema futuro o trouxer, entra por `tone` sem mudar a API.
- **Determinismo e custo.** Só `useCurrentFrame`; sem `Math.random`, sem filtro, sem `blur`, sem sombra difusa [I].
- **Bordas.** Sem marcos: não desenha. Marcos com o mesmo `at`: ordem estável e blocos separados pelo `placeLabels`. `bands` com tamanho errado: as que faltam são `base`, as que sobram são ignoradas. `tickFrames` curto: o resto segue o `stagger`.
- **Função pura `limitMeterLayout`** (posições, larguras, deslocamentos dos blocos, altura total) exportada e testada à parte, como `splitLayout` e `floatingMotion` [F].
- **Fora de escopo da v1:** orientação vertical ("termômetro"), escala logarítmica, mais de 3 marcos, rótulos das pontas da escala (o fim da escala é margem, não dado), contagem rolando no valor.

## 4. Camada B: a emenda às ADR 011 e 014 (texto proposto)

**Uma só emenda, junto com a `ValueTable`** ("infográficos em retrato"); o texto da `table` está na §4 de `value-table.md`. Para o `limit`:

1. Novo tipo `limit` (componente do kit: `LimitMeter`; afirmação na tela: `claims` obrigatórias):
   - `title`; `ticks` (de **1 a 3**: `at`, `value`, `label`, `anchor?`); `bands` (vazio ou **`ticks + 1`**: `label` padrão vazio, `tone`: `base` | `emphasis`); `marker?` (`at`, `value`, `label`, `anchor?`); `scale_min` (padrão 0) e `scale_max?`.
   - `value` segue a regra do `number`, do `compare` e da `table`: o texto como aparece na tela, sem conversão. **`at` não aparece na tela**: é a posição na escala.
2. Validação (erro em `scenes.json` e em `episode.json`): `at` dos marcos **estritamente crescente** e rótulos únicos; tudo dentro de `[scale_min, scale_max]`; `bands` vazio ou com `ticks + 1` itens; `anchor` em um marco ⇒ em **todos** os marcos **e** no marcador (se houver), em ordem na narração e depois da âncora do plano.
3. **`value` e `at` podem divergir** (erro de digitação: "R$ 81 mil" com `at: 18000`). O contrato não tem como saber; **quem confere é o agente `verificador`** (cada `value` e `label` contra os trechos; `at` contra `value`). **Não** derivar `at` do texto: "R$ 81 mil" e "R$ 97.200" exigiriam interpretar "mil" como ×1000, e o template **nunca converte** (ADR 011, decisão 7).
4. `claims`: as do plano (herdadas de `_FactualShot`, no mínimo uma), como na `table` (por isso o `vp check` as percorre). O texto das faixas só diz o que a ficha diz; **o marcador só entra com valor de ficha**.
5. `episode.json`: `steps_ms` passa a valer também para `limit` **com `anchor`**: um tempo por marco e, se houver, um para o marcador (`len(ticks) + 1`). **Mudar o `episode.json` exige esta ADR** (`CLAUDE.md` §6).

**ADR 014, emenda:** `limit` entra em `PORTRAIT_SHOT_KINDS` (junto com `table`: de 8 para 10 planos em retrato).

**Decisão aberta registrada:** `limit` como **plano novo** (recomendado) ou como `chart` com `type: "limit"`. **Recomendo o plano novo:** o `chart` guarda pontos **numéricos** e deixa o kit formatá-los (`formatValue`, com `pt-BR` por padrão), enquanto o `limit` precisa do **texto da ficha** ("R$ 81 mil", "US$ 20.000"); com 6 das 10 verticais em inglês, o texto pronto evita o separador errado: hoje `screen_number`, o `Odometer` do template e os gráficos só entendem o formato pt-BR (`"US$ 20,000"` vira 20; ver `value-table.md` §7, item 6) [F, testado].

## 5. Camada C: contrato, `vp check`, adaptador e template

### 5.1 Schema (`app/pipeline/schemas.py`)

```python
LIMIT_MAX_TICKS = 3

class LimitTick(Model):
    at: float          # posição na escala; só geometria, não aparece na tela
    value: NonEmpty    # texto como aparece na tela: "R$ 81 mil"
    label: NonEmpty    # o que o limite é: "Limite anual"
    anchor: NonEmpty | None = None

class LimitBand(Model):
    label: str = ""
    tone: Literal["base", "emphasis"] = "base"

class LimitMarker(Model):
    at: float
    value: NonEmpty
    label: NonEmpty
    anchor: NonEmpty | None = None

class LimitShot(_FactualShot):
    kind: Literal["limit"] = "limit"
    title: NonEmpty
    ticks: list[LimitTick] = Field(min_length=1, max_length=LIMIT_MAX_TICKS)
    bands: list[LimitBand] = []
    marker: LimitMarker | None = None
    scale_min: float = 0
    scale_max: float | None = None
    # validadores: `at` crescente; rótulos únicos; tudo dentro da escala; `bands` vazio ou ticks + 1;
    # âncoras em todos os marcos e no marcador, ou em nenhum
```

`Shot` ganha `| LimitShot`; `PORTRAIT_SHOT_KINDS` e `GRAPHIC_SHOT_KINDS` ganham `"limit"` (tela cheia, como o `chart`; fora de `OVERLAY_SHOT_KINDS`). `EpisodeShot._steps_match` e `step_positions` aceitam o plano (§4, item 5). O espelho em `video/src/types.ts` ganha `LimitSpec`.

### 5.2 `vp check` (`app/pipeline/check.py`, `text_fit.py`)

| Regra | Valor proposto | Base |
|---|---|---|
| Tempo de leitura | `limit` em `READING_KINDS` (mínimo de 4 s) | [F] `READING_MS = 4000` |
| Valor do marco | `LIMIT_VALUE = (12, 1)` | [I] bloco de até 280 px, letra 40 em negrito, ≈0,55 de largura média |
| Rótulo do marco | `LIMIT_LABEL = (20, 2)` | [I] mesmo bloco, letra 26, ≈0,5 |
| Texto da faixa | `LIMIT_BAND = (20, 2)` | [I] a mesma caixa |
| Variedade | conta como plano gráfico; "o mesmo tipo duas vezes" e `MAX_GRAPHIC_RUN` já valem | [F] `variety_warnings` |
| Marcos demais | 3 marcos × 280 px + folgas ≈ 870 px: cabe em 940 px, com 4 não | [I] por isso o teto de 3 |

Os limites são estimativa (a mesma de `text_fit.py`) e **precisam ser conferidos em quadros**; o caso 1 é o teste de fogo.

### 5.3 Adaptador e template

- **Adaptador (`app/render/remotion.py`, `_editorial`):** `limit` com `anchor` emite `stepFrames` (um por marco e, se houver, o do marcador), como a rede e a `table`.
- **Template (`video/src/Editorial.tsx`, `ShotView.tsx`, `types.ts`):** `LimitShot` segue o `ChartShot` [F]: mesmo contêiner, `Title` com o título do plano, a régua **alinhada ao topo do espaço útil** (como o gráfico em retrato, `alignItems: flex-start`). Em retrato: `width={kit(940)}`, `valueSize={kit(40)}`, `labelSize={kit(26)}`, `trackHeight={kit(28)}`; em paisagem, os defaults do kit. `enter="rise"` (a régua não muda); `tickFrames`/`markerFrame` vêm de `stepFrames`. A fonte do rodapé sai das `claims` [F, `shots.py`].
- **Apresentador (`app/media/host.py`, `blocked_corners`):** em retrato, `limit` **bloqueia os dois cantos de cima** (o título e a régua ocupam o topo) e, como o `chart`, **não conta como conteúdo centralizado**: numa cena só de gráficos, tabelas e réguas os cantos de baixo ficam livres. Em paisagem, bloqueia o canto de cima à esquerda (o título). Muda a regra, muda o teste de `host.py`. **Esta linha faltava na primeira versão da spec.**
- **Skills e docs:** `roteiro-explicativo/SKILL.md` ("a frase fala de um limite, teto ou piso e do que acontece de cada lado → `limit`") e `planos.md` (seção `limit`, com os casos 1 a 3); `checagem/SKILL.md` (cada `value` e `label` contra o trecho; `at` coerente com `value`; texto de faixa só com o que a ficha diz; marcador só com valor de ficha; nenhuma margem restante ou percentual do limite); `CLAUDE.md` §6 (lista de planos do retrato).

## 6. Testes e aceite

**Kit (`src/charts/LimitMeter.test.ts(x)`, `node:test`; `renderAtFrame` como em `Pane.test.tsx` [F])**

1. `limitMeterLayout`: posição proporcional; **marcos a 130 px de distância com blocos largos são afastados**, ficam dentro de `[0, width]` e sem sobreposição; os que já cabem não se mexem; valores fora da escala são limitados às pontas.
2. Antes de `tickFrames[i]` o marco e a faixa à esquerda não aparecem (o espaço fica reservado); no quadro dele, o marco; `cut` mostra a faixa cheia num quadro, `rise` a mostra parcial dois quadros depois.
3. A faixa `emphasis` leva a hachura e `theme.accent`; `base`, não.
4. O marcador entra depois do último marco e fica numa linha própria.
5. Com um tema de cores trocadas, a saída usa **só** as cores do tema (nenhuma cor escrita no componente).
6. Determinismo (o mesmo quadro, o mesmo HTML) e tamanhos em 1080×1920 por `useUnit`.
7. `bands` com tamanho errado e `tickFrames` curto não quebram.

**Revisão visual (kit):** `npm run still` em início, meio e fim de cada demo, em paisagem e em retrato, com **o caso de marcos próximos** (neutro, mesma geometria do MEI) à vista (`AGENTS.md`: "renderização bem-sucedida não certifica qualidade visual").

**Contrato e template (`tests/`, padrão de `test_editorial_shots.py` [F])**

1. Planos válidos nos três casos da seção 2, com `claims`, em retrato e em paisagem.
2. Erros: `at` fora de ordem ou repetido; rótulos repetidos; mais de 3 marcos; `bands` com tamanho errado; marcador fora da escala; âncoras só em alguns itens; plano sem `claims`.
3. `episode.json`: `steps_ms` com `ticks + marcador` tempos, em ordem e dentro do plano.
4. `portrait_problems` aceita `limit`; `text_fit` e leitura mínima de 4 s.

**Régua:** a folha de quadros do vídeo-régua **não deve mudar** (nenhum plano existente muda), com sonda de CPU antes. O visual do `limit` se revê num quadro parado; **render só com autorização do dono**.

## 7. Riscos e decisões abertas

| # | Questão | Para decidir |
|---|---|---|
| 1 | Plano novo `limit` (recomendado) ou `chart` com `type: "limit"` | dono, na ADR |
| 2 | **`at` e `value` divergem sem o contrato notar** | o `verificador` confere; vale um teste de aceite por caso |
| 3 | `emphasis` = destaque dourado com hachura, sem "vermelho de alerta" (o editorial só tem um destaque) | dono, junto com a decisão sobre uma segunda identidade |
| 4 | Marcador com exemplo hipotético ("quem faturou R$ 90 mil") | exige ADR própria; hoje, só valor de ficha |
| 5 | O afastamento dos blocos (`placeLabels`) em marcos muito próximos pode ficar poluído | validar no caso 1 em quadro renderizado |
| 6 | Limites de texto (`LIMIT_VALUE`, `LIMIT_LABEL`, `LIMIT_BAND`) são estimativa | conferir em quadros |
| 7 | Teto de 3 marcos | medir; 4 só em paisagem, se um dia precisar |
| 8 | Escala a partir de 0 vs. início livre (`scale_min`) | a faixa "dentro do limite" nasce do 0; manter 0 como padrão |
| 9 | Dependências: a PR de tokens de movimento (opcional) e a **ADR conjunta com a `table`** | decidir as duas juntas |
| 10 | Esforço: kit ≈ médio (o layout dos blocos é a parte difícil); B, só texto; C ≈ médio | [I] estimativa relativa, sem dias |

## 8. Ordem de entrega

1. **PR do kit** (camada A): componente, `limitMeterLayout`, demos e testes; mostrar os quadros antes do merge. Pode andar **em paralelo** com a PR da `ValueTable`.
2. **PR de docs** (camada B): a emenda conjunta às ADR 011 e 014 (`table` e `limit`), para o dono decidir as questões 1, 3 e 4.
3. **PR do template e do contrato** (camada C): schema, `vp check`, `text_fit`, adaptador, template, skills, testes e o pin novo do kit (`CLAUDE.md` §14: cruzar o SHA do pin com o checkout). Vídeo-régua e sonda de CPU.
