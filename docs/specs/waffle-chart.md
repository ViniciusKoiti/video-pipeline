# Spec: variante `waffle` do `ShareChart` (motion-kit) e o campo `variant` do plano `chart`

- **Estado:** rascunho para aprovação do dono (2026-10-07). **Nada aqui está implementado.** Onde diz **decisão aberta**, o agente não decide: pergunta ao dono. Em conflito valem `CLAUDE.md`, as ADRs e o `AGENTS.md` do kit.
- **Origem:** item 5 de `docs/pesquisa/componentes-infografico-2026-10.md`. É a menor das peças da camada de Infographic: **uma terceira variante de um componente que já existe**, não um componente novo.
- **Irmã das specs da `ValueTable`, do `LimitMeter` e do `RevealList`** (`docs/specs/`): o que é igual (as três camadas, os entregáveis do kit, a emenda conjunta às ADR 011 e 014, o aviso de idioma) **não se repete aqui**.
- **Rótulos:** [F] confirmado em arquivo; [I] inferência; [H] hipótese a medir.
- **Três camadas:** **A** a variante no kit; **B** a emenda às ADR 011 e 014 (a mesma dos outros três); **C** o campo `variant` no plano `chart`, o `vp check`, o adaptador e o template.

## 1. O que é, e o que não é

**É** uma grade de **100 quadrados** em que a fração de uma parte aparece preenchida: "63 em cada 100". Mostra uma **proporção de pessoas ou coisas** em escala humana, que uma barra de 100% não passa.

**Por que existe:** os formatos mapeados têm várias afirmações do tipo "X% de uma população" (`componentes-infografico-2026-10.md` §2, item 5): **63% dos adultos cobririam uma despesa de US$ 400** (Fed, SHED 2025), **60,2% dos adultos dos EUA usam suplemento** (NCHS, 2026), 56% dos trabalhadores dos EUA já usaram IA no trabalho (Census). Hoje o `chart` com `type: "share"` só desenha **a barra de 100%** (`variant="bar100"` fixo em `Editorial.tsx`, l. 216 [F]).

**Não é:** gráfico para muitas partes (no máximo 3, mais o "resto"), para frações menores que 1% (somem na grade), nem para valores que não são percentuais.

**Quando usar [I]:** **uma ou duas partes** de uma população ("63% fazem X") → `waffle`; partes de um todo de tamanhos diferentes e rótulos longos → `bar100`; muitas partes → a barra, não a grade.

## 2. A regra que mais importa: o "resto" não ganha número na tela

O kit já calcula a fatia que sobra (`whole - sum`, `ShareChart.tsx` l. 118 a 123 [F]) e a desenha **com o valor escrito** ("Outros 37%"). A ficha do Fed diz o oposto [F, `nichos-globais-anexos/financas-ficha.md` §8]: **"não mostrar '37%' (subtração; inclui quem pagaria no cartão)"**: o restante é gente que pagaria de outro jeito **ou não cobriria**, e o texto lido não decompõe. Num waffle de uma parte, o "resto" ocupa 37 dos 100 quadrados e **qualquer número escrito nele seria derivado** (ADR 011, decisão 7).

**Regra do waffle:** a parte que sobra é desenhada como quadrados neutros, **com rótulo mas sem valor**, a menos que uma ficha traga o número: aí ele entra como **texto pronto** (`restValue`). Os valores das partes listadas continuam saindo de `formatValue` com o `locale`, como no `ShareChart` de hoje.

## 3. Camada A: a variante no kit

**Onde:** `src/charts/ShareChart.tsx`, que passa a aceitar `variant: 'bar100' | 'donut' | 'waffle'`. As fatias, a entrada em sequência (a destacada por último), `highlight`, `rest`, `total`, `unit`, `decimals`, `locale`, `delay`, `stagger` e `growDuration` **valem como estão** [F]. Entregáveis como os da `ValueTable` (§3.3 daquela spec): uma demo `ShareChartWaffleDemo.tsx` (paisagem e retrato), com **dados neutros**, quadros em `examples/stills.json`, atualização da linha de `ShareChart` em `COMPONENTS.md`, `npm run check`, build e `dist/`.

### 3.1 Props acrescentadas

```ts
export interface ShareChartProps {
  // ... as existentes ...
  /** `'bar100'` (default), `'donut'` ou `'waffle'`. */
  variant?: 'bar100' | 'donut' | 'waffle';
  /** Só `waffle`: colunas e linhas da grade. Default: 10 × 10 (100 células). */
  columns?: number;
  rows?: number;
  /** Só `waffle`: onde ficam os rótulos. `'right'` (default) ou `'below'`. */
  legend?: 'right' | 'below';
  /** Só `waffle`: texto pronto do valor da parte que sobra ("37%"), se uma ficha o traz.
   *  Sem ele, a parte que sobra aparece com o rótulo e sem número. */
  restValue?: string;
}
```

### 3.2 Comportamento

- **Células.** `N = columns × rows`. A fatia `k` (com `start` e `share`) ocupa as células de `round(start × N)` a `round((start + share) × N)` (**arredondamento acumulado**: a soma dá sempre `N` e cada fatia erra menos de 1 célula). **Com `N = 100`, uma célula é um ponto percentual**; o valor exato está no rótulo ("60,2%" ocupa 60 células). Ordem de preenchimento: leitura, da esquerda para a direita e de cima para baixo. A função pura `waffleCells(slices, columns, rows)` devolve a fatia de cada célula e é testada à parte [I].
- **Entrada.** Cada fatia preenche as suas células em `growDuration` quadros a partir do seu `at` (célula a célula, na ordem de leitura); **a destacada entra por último**, como na barra [F]. O rótulo da fatia aparece junto (`shown(s)`). O `ShareChart` não tem a prop `enter` das outras peças: a entrada é por `growDuration`, e um valor de 1 faz tudo num quadro [I].
- **Cores.** As mesmas da barra [F]: a fatia destacada em `theme.accent`, as outras em tons neutros de `theme.muted`, o resto em `muted` a 20%. **Nenhuma cor escrita no componente.** A fatia destacada se distingue **também pela posição na ordem de entrada**, não só pela cor [I].
- **Célula.** Quadrada, de lado `(largura disponível − folgas) ÷ columns`, folga de 4 px; cantos retos (o `emphasis` do editorial não tem raio). Células vazias em `theme.line`.
- **Rótulos (`legend`).** Linhas empilhadas: **amostra da cor, valor (negrito, `tabular-nums`) e rótulo**. `'right'`: coluna à direita da grade (paisagem, 10 × 10). `'below'`: abaixo da grade (retrato, 20 × 5). O valor da parte que sobra só aparece com `restValue` (seção 2).
- **Determinismo e custo.** Só `useCurrentFrame`; 100 `rect` SVG por quadro; sem filtro, sem `blur` [I].
- **Bordas.** `N` diferente de 100: avisa-se na documentação que a célula deixa de ser 1 ponto percentual; a variante funciona. Fatia que arredonda para 0 célula não aparece (o contrato recusa partes abaixo de 1%).
- **Fora de escopo:** pictograma com ícones de pessoa (exigiria ícone por quadrado), mais de 3 partes, `donut` no retrato (a altura padrão de 760 px não cabe nos ≈560 px úteis [F, `ChartShot`]).

## 4. Camada B: a emenda às ADR 011 e 014 (texto proposto)

**Uma só emenda, junto com `table`, `limit` e `list`** ("infográficos em retrato"). Para o `chart`:

1. **Campo novo em tipo existente** (tabela "Campos novos em tipos existentes" da ADR 011): `chart`: `variant` (`bar100` | `waffle`, só `share`; ausente = `bar100`, o que o template faz hoje) e `rest_value?` (texto pronto do valor da parte que sobra, só `share` com `variant: "waffle"`).
2. Regras de validação (erro em `scenes.json` e em `episode.json`): `variant` só com `type: "share"`; `waffle` exige `unit` igual a `"%"`, **no máximo 3 partes**, **cada parte com pelo menos 1** e a soma das partes **menor ou igual a 100**; com `rest`, o resto fica com o que falta; sem `rest`, a soma tem de ser 100 (±0,5), senão o contrato recusa (a grade não pode parecer "63 de 100" quando a soma é 63); `rest_value` só com `rest`.
3. **A ficha é quem dá o número do resto.** Sem `rest_value`, a tela não escreve o valor da parte que sobra; **`verificador`** confere que nenhum número derivado foi acrescentado.
4. `episode.json`: o campo novo é do plano (`spec`), e **mudar o `episode.json` exige esta ADR** (`CLAUDE.md` §6). Não há tempo por passo: a entrada do `ShareChart` é por duração, não por âncora.
5. **Nome do campo:** `variant`, como a prop do kit (a primeira versão do levantamento dizia `look`).

**ADR 014, emenda:** nada muda na lista de planos do retrato (`chart` já está nela); a emenda registra só o arranjo da grade em retrato (seção 5.3).

**Decisão aberta registrada:** expor também `donut` no `variant` do contrato (o kit já o tem). Recomendo **não** expor agora: a altura da rosca não cabe no retrato, e nenhum formato mapeado a pede.

## 5. Camada C: contrato, `vp check`, adaptador e template

### 5.1 Schema (`app/pipeline/schemas.py`)

`ChartShot` ganha dois campos opcionais, com validadores novos:

```python
    variant: Literal["bar100", "waffle"] | None = None   # só `share`; sem ele, `bar100`
    rest_value: str | None = None                        # só `share` com `waffle`: texto pronto do resto
    # validadores: `variant` só com `type == "share"`; `waffle`: unit "%", até 3 partes, cada uma >= 1,
    # soma <= 100 (com `rest`) ou == 100 ±0,5 (sem `rest`); `rest_value` só com `rest`
```

O espelho em `video/src/types.ts` (`ChartSpec`) ganha `variant?` e `rest_value?`.

### 5.2 `vp check` (`app/pipeline/check.py`, `text_fit.py`)

| Regra | Valor proposto | Base |
|---|---|---|
| Rótulo de cada parte | `WAFFLE_LABEL = (50, 2)` (caracteres por linha, linhas) | [I] em retrato, linha de ~760 px (940 menos amostra e valor), letra 26 (≈13 px por caractere → 58; usar 50) |
| Tempo de leitura | `chart` já está em `READING_KINDS` (mínimo de 4 s) | [F] |
| Uma parte e o resto | com `waffle` e uma parte só, **alerta** se o título repete o número da parte (a tela diria "63%" duas vezes) | [H] |
| Variedade | continua gráfico (`MAX_GRAPHIC_RUN`, "o mesmo tipo duas vezes") | [F] |

### 5.3 Adaptador e template

- **Adaptador:** nada muda (o `spec` do plano já é repassado inteiro; `model_dump` [F] leva `variant` e `rest_value`).
- **Template (`video/src/Editorial.tsx`, `ChartShot`, ramo `share`):** `variant={spec.variant ?? "bar100"}`; no `waffle`, em **retrato**: `columns={20}`, `rows={5}`, `legend="below"`, largura de 920 px (célula de 42 px mais folga de 4); em **paisagem**: 10 × 10 e `legend="right"`. `restValue={spec.rest_value}`. Altura em retrato ≈ 230 px de grade mais ≈ 190 px de rótulos: cabe nos ≈560 px úteis [I, conta sobre o `ChartShot`].
- **`locale`:** hoje o template **não** passa `locale` ao `ShareChart` (usa `pt-BR`) [F]; **o waffle em inglês depende da correção de idioma** (`episode.language` até o template; `docs/specs/value-table.md` §7, item 6). Sem ela, "60.2%" sairia "60,2%".
- **Apresentador (`app/media/host.py`):** **sem mudança**: o plano continua sendo `chart`, que já bloqueia os cantos de cima em retrato [F].
- **Skills e docs:** `roteiro-explicativo/planos.md` (seção `chart`: quando usar `waffle`, com os casos 1 e 2 e a regra do resto); `checagem/SKILL.md` (nenhum número derivado no resto; unidade `%`; partes de 1% a 99%); `CLAUDE.md` não muda.

## 6. Casos de aceite (dados reais, só no template; o kit usa dados neutros)

| # | Título | Partes | Resto | Fonte |
|---|---|---|---|---|
| 1 | Reserva de emergência nos EUA | 63% "Cobririam uma despesa de US$ 400 com dinheiro ou equivalente" | rótulo "Os demais", **sem número** | Fed, SHED 2025, página atualizada em 2026-05-13 (`nichos-globais-anexos/financas-ficha.md`) |
| 2 | Uso de suplemento nos EUA | 60,2% "Tomaram suplemento nos últimos 30 dias" (60 células; o rótulo diz 60,2%) | rótulo "Os demais", **sem número** | CDC/NCHS, Data Brief 561, 2026-05 (`nichos-globais-anexos/nutricao-ficha.md`) |
| 3 | (neutro) | 47%, 29% e 3%, mais o resto | com `restValue` | caso de arredondamento acumulado e de rótulo de fatia pequena |

## 7. Testes

**Kit (`src/charts/ShareChart.test.tsx`, `node:test`, `renderAtFrame`; padrão de `Pane.test.tsx` [F])**

1. `waffleCells`: 63 e resto → 63 células da parte e 37 do resto; 60,2 → 60; 47 + 29 + 3 + resto → total exato `N`; **a soma é sempre `N`**; ordem de leitura; 20 × 5 equivale a 10 × 10 em contagem.
2. Antes do `at` da fatia, as células dela não estão preenchidas; ao fim de `growDuration`, todas; **a destacada entra por último**.
3. A parte que sobra **não tem número** sem `restValue`; com ele, o texto pronto aparece como veio.
4. Só cores do tema (tema de cores trocadas); determinismo; tamanhos em 1080×1920.
5. A variante `bar100` **não muda** (regressão: o mesmo HTML de antes nos quadros de uma demo).

**Revisão visual (kit):** `npm run still` em início, meio e fim da demo, em paisagem e em retrato.

**Contrato e template (`tests/`, padrão de `test_editorial_shots.py` [F])**

1. `chart` com `variant: "waffle"` válido nos casos 1 a 3, em retrato e em paisagem.
2. Erros: `variant` em `bar` ou `line`; unidade diferente de `%`; mais de 3 partes; parte menor que 1; soma acima de 100; soma diferente de 100 sem `rest`; `rest_value` sem `rest`.
3. **Regressão:** `chart` com `share` sem `variant` continua `bar100` (nenhum `episode.json` existente muda).

**Régua:** a folha de quadros do vídeo-régua **não deve mudar** (nenhum plano existente muda), com sonda de CPU antes; **render só com autorização do dono**.

## 8. Riscos e decisões abertas

| # | Questão | Para decidir |
|---|---|---|
| 1 | **O "resto" sem número** (seção 2): é a regra do projeto, mas a barra de 100% de hoje o mostra | dono, na ADR; vale decidir se a barra também deixa de mostrar o resto sem `rest_value` |
| 2 | Erro de até 1 ponto percentual na grade (60,2 vira 60 células) | o rótulo carrega o valor exato; aceitar, ou preencher a última célula parcialmente (mais código) |
| 3 | Waffle de uma parte repete o número se o título também o diz | alerta do `vp check` [H] |
| 4 | Expor `donut` | recomendo não |
| 5 | **Idioma:** o `ShareChart` formata com `locale` e o template não o passa | depende da correção de idioma (bloqueia o inglês) |
| 6 | Limite de texto (`WAFFLE_LABEL`) é estimativa | conferir em quadro |
| 7 | Esforço: kit ≈ pequeno a médio (legenda e entrada); B, só texto; C ≈ pequeno | [I] estimativa relativa, sem dias |

## 9. Ordem de entrega

1. **PR do kit** (camada A): `waffleCells`, a variante e a demo; mostrar os quadros antes do merge. Pode andar em paralelo com os outros.
2. **PR de docs** (camada B): a emenda conjunta às ADR 011 e 014.
3. **PR do template e do contrato** (camada C): `ChartShot`, o ramo de `share`, skills e testes; **com a correção de idioma antes, se o inglês for o primeiro uso**.
