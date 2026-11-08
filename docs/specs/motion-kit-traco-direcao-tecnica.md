# Direção técnica: traço à mão no motion-kit

Data: 2026-11-03. Base: `docs/pesquisa/traco-desenho-series-2026-11-03.md` (o que falta) e o protótipo em
`video/src/quadro/` (o que já funciona). Este documento diz **como** construir, não o que construir.

## 0. Resumo

- Quatro peças novas no kit, em ordem: `InkStroke`, o atraso de cor no `DrawPath`, `PenTip` e `Erase`. Depois,
  `FillLevel`, `LabelBox`, `TextReveal` e `StackBuild`. `StickLimbs` fica para depois da decisão sobre o corpo.
- O `Board` (quadro que persiste entre cenas) fica no template, não no kit, até existir ADR do contrato.
- Quase tudo é reuso: `DrawPath`, `SoftMask`, `Stepped`, `Overprint`, `PatternFill`, `StyleTexture`, `drift`,
  `Odometer`, `arrowHead`, `measureTextFit`, `fitTextOnNLines` e as funções de `@remotion/paths`.
- Correção de uma afirmação da entrada: "com `taper` 0 o resultado é igual ao `DrawPath`" não vale no nível do
  texto do SVG, porque as implementações são diferentes (máscara de tracejado contra polígono). A aceitação é
  **visual**: stills nos mesmos quadros, com diferença abaixo de um limite definido.

## 1. Princípios

1. **Determinismo.** Todo resultado é função do quadro global e de sementes fixas. Nada de `Math.random` nem de
   contador de chamadas. Sem isso, a cache por cena e a vídeo-régua não funcionam.
2. **Geometria pura separada do React.** Cálculo em módulos sem Remotion, testáveis com o runner de testes.
3. **Estilo manda.** Espessura, tremor, cor e fonte vêm de `useStyle()`, `useMotionTheme()` e `useUnit()`. Nenhum
   número solto no componente.
4. **Um `<svg>` por bloco, não um por traço.** O protótipo cria uma camada por traço; isso não escala. O kit compõe
   `<g>` dentro de um único `<svg>` por caixa.
5. **Sem mão.** Nenhuma peça desenha uma mão. O substituto é `PenTip`, uma forma genérica.

## 2. Camada geométrica (kit)

Módulo novo: `src/styles/primitives/inkGeometry.ts`, puro, com teste `inkGeometry.test.ts` ao lado.

- **`samplePath(d, n)`**: converte um `d` do SVG em `n` pontos equidistantes, com `getLength` e `getPointAtLength`
  de `@remotion/paths` (peer já declarado). Memoizar por `d` e `n`: `getLength` é caro e não deve rodar a cada quadro.
- **`pointsAt(points, progress)`**: prefixo do polígono até a fração `progress`, com o último ponto interpolado.
  Equivale ao `pontosAte` do protótipo.
- **`tremor(points, amplitude, seed, frame, every)`**: deslocamento por ruído, usando `boilSeed` e `wobblePoint` de
  `linePath.ts`. Assim `InkStroke` e `DrawPath` tremem do mesmo jeito. Sai o `ruido` próprio do protótipo.
- **`taperOutline(points, width, taper, closed)`**: contorno em polígono. Aberto: espessura `w(t) = width *
  (1 - taper + taper * sin(pi t)^0.5)`, com `taper` de 0 a 1. Fechado: dois anéis com `fillRule="evenodd"`.
- Tamanho de amostragem: `n = clamp(length / 6, 40, 400)` px. Abaixo de 40, a curva fica poligonal; acima de 400,
  o custo por quadro sobe sem ganho visual.

## 3. Componentes

Para cada item: arquivo, props, implementação e aceitação.

**3.1 `InkStroke`** (`styles/primitives/InkStroke.tsx`)
- Props: `d` ou `points`, `width`, `height`, `at`, `duration`, `color`, `strokeWidth`, `taper`, `wobble`,
  `boilEvery`, `seed`, `closed`, `style`.
- Implementação: amostra o caminho, aplica tremor, revela até `progress` (com `easing` igual ao `DrawPath`) e gera
  o contorno com `taperOutline`. Um único `<path>` por traço.
- Aceitação: `taper` 0 e `closed` falso igual ao `DrawPath` visualmente (stills nos quadros 0, 12, 24 e 48,
  diferença média abaixo de um limite a definir com o dono).

**3.2 Atraso de cor no `DrawPath`** (alteração em peça existente)
- Hoje `fill` aparece com `opacity={progress}`, junto com o traço. Acrescentar `fillAt` e `fillDuration`. Default:
  os valores atuais (aparece junto). Sem default novo, nenhum vídeo atual muda.
- Aceitação: teste de regressão (props default produzem a mesma árvore) e still com `fillAt` depois do fim do traço.

**3.3 `PenTip`** (`styles/primitives/PenTip.tsx`)
- Props: `d`, `at`, `duration`, `shape` (`dot` ou `triangle`), `size`, `color`.
- Implementação: posição e ângulo com `getPointAtLength` e `getTangentAtLength` no comprimento `progress * getLength(d)`.
  Visível só entre `at` e `at + duration`: some por desmontagem, não por opacidade.
- Aceitação: a ponta coincide com o fim do traço revelado em três quadros de teste.

**3.4 `Erase`** (`styles/primitives/Erase.tsx`)
- Props: `at`, `duration`, `angle`, `feather`, `children`.
- Implementação: `SoftMask` com `shape: 'wipe'` e `progress` decrescente de 1 a 0. Ao terminar, o elemento é
  desmontado. Assim, o apagamento não deixa resto no DOM.
- Aceitação: still no meio do apagamento mostra a borda macia; depois do fim, o elemento não aparece no DOM.

**3.5 `FillLevel`** (`components/FillLevel.tsx`)
- Props: `outline` (`d` ou `points`), `levels` (`[{at, to}]`, de 0 a 1), `duration`, `color`, `wave`, `steps`.
- Implementação: `clipPath` em SVG com `useId` e o contorno, e um retângulo cujo topo sobe. Usar `clipPath` do SVG,
  não `clip-path` do CSS: o SVG antialias igual ao contorno. Os degraus vêm de `steppedFrame`. A onda é uma
  polilinha senoidal que treme com `boilSeed`.
- Aceitação: still com nível em 0, 0,5 e 1, com o líquido recortado na forma do contorno.

**3.6 `LabelBox`** (`components/LabelBox.tsx`)
- Props: `text`, `width`, `height`, `at`, `color`, `padding`.
- Implementação: borda com `DrawPath` (retângulo com tremor). O texto entra com `TextReveal` depois que a borda
  termina (`at + duration`). O tamanho da fonte vem de `measureTextFit` (já no kit, em `editorial/textLayout.ts`)
  ou de `fitTextOnNLines` (`@remotion/layout-utils`, peer já declarado).
- Aceitação: texto nunca passa da borda em três tamanhos de texto diferentes.

**3.7 `TextReveal`** (`components/TextReveal.tsx`)
- Props: `children` (texto), `at`, `duration`, `angle`, `feather`.
- Implementação: `SoftMask` com `shape: 'wipe'`, `progress` de 0 a 1. Revelação por palavra fica para uma segunda
  versão, com `CaptionText`. Por máscara, o texto não precisa de medida glifo a glifo.
- Pré-condição: a fonte carregada antes do primeiro quadro (`delayRender`/`continueRender`, como o `Clipe`).
- Aceitação: still no meio da revelação com a borda macia; fonte de fallback nunca aparece (teste com a fonte
  carregada e sem ela).

**3.8 `StackBuild`** (`components/StackBuild.tsx`)
- Props: `items` (lista de conteúdos), `start`, `step`, `children` ou `renderItem`.
- Implementação: cada item aparece em `start + i * step`, com `Stepped` para os passos. Puro, sem estado.
- Aceitação: ordem e tempos conferidos em teste de função (`stackTimes(n, start, step)`).

**3.9 `StickLimbs`** (depois da decisão sobre o corpo)
- Props: `shoulder`, `hand`, `upper`, `lower`, `bend`, `at`, `duration`, `color`.
- Implementação: cinemática de dois ossos. Dados o ombro, a mão e os comprimentos, o cotovelo sai da lei dos cossenos
  (com o sinal de `bend` para o lado). O resultado é uma polilinha que vai para `InkStroke`.
- Aceitação: o comprimento total do membro é constante em todos os quadros (teste).

**3.10 `Board`** (template, `video/src/quadro/`, não o kit)
- Função pura: `boardState(globalFrame, elements)` devolve o que está visível e o progresso de cada elemento.
- Cada cena recebe `globalStart` nas props. Assim, a cena inicial já mostra o quadro no estado certo, sem um
  quadro de transição.
- A cache por cena (`app/render/remotion.py`) precisa incluir as entradas do `Board` na chave. Sem isso, duas cenas
  com o mesmo quadro e estados diferentes reaproveitam o mesmo arquivo.
- Corte limpo entre cenas: sem fade. A continuidade do quadro vem do estado, não de uma transição.

## 4. Contrato e plano (template e pipeline)

- Novo tipo de plano `board` em `video/src/types.ts` (união `ShotSpec`), `ShotView` e no schema do pipeline
  (`app/pipeline/schemas.py` ou o módulo em `app/<área>/models/`, uma classe por arquivo, ADR 037).
- Validação no `vp check`: cada passo do quadro cai numa palavra da narração (âncora, ADR 008); os passos de um
  elemento estão em ordem; nenhum elemento aparece antes da primeira menção.
- Mudar o `episode.json` exige ADR (CLAUDE.md §6). A ADR do `board` deve vir antes da primeira cena que o usa.
- O motor continua o do `explainer` (ADR 001). Não há motor novo.

## 5. Versão e pacote

- Kit `0.8.0`: `InkStroke`, atraso de cor no `DrawPath`, `PenTip`, `Erase`, `FillLevel`, `LabelBox`, `TextReveal`,
  `StackBuild`.
- Kit `0.9.0`: `StickLimbs`, depois da decisão sobre o corpo.
- `Board` fica no template até a ADR. Depois, avaliar se vira peça do kit.
- Processo: ADR 027 (tarball em `video/vendor/`), `CHANGELOG`, `dist` com `tsup`, e vídeo-régua em cada versão.

## 6. Testes

- **Geometria (kit):** funções puras em `inkGeometry.test.ts`, sem navegador. Casos: amostragem de uma reta e de um
  círculo; `pointsAt` nos extremos; `taperOutline` com `taper` 0 e 1; `stackTimes`; comprimento constante do membro.
- **Visual (kit):** stills de cada componente em quadros fixos, comparados com linhas de base aprovadas pelo dono.
  Não são testes automáticos de aparência; são conferidos em revisão.
- **Template:** `node --test` em `video/tests/` para `boardState` (já há o padrão em `labels.test.ts`).
- **Contrato (pipeline):** testes em Python para o `vp check` das âncoras do `board`, sem rede (CLAUDE.md §2.10).

## 7. Desempenho

- Máquina limitada: a sonda `cpu_probe` (CLAUDE.md §3, acima de 0,3 s) antes de qualquer render longo.
- Memoizar `samplePath` por `d`. Ele não roda a cada quadro.
- Um `<svg>` por caixa. Não criar uma camada por traço.
- Reduzir a fervura (`boilEvery`) em cenas longas, se o tempo de render passar do limite do vídeo-régua.
- Medir o tempo por cena e registrar em `data/benchmarks/`.

## 8. Riscos técnicos

- `getLength` e `getPointAtLength` em caminhos longos podem ser lentos. A memoização resolve na maioria dos casos.
- Máscara `wipe` e `clipPath` antialiasam de forma diferente entre navegadores. O render usa o Chrome headless do
  projeto; o teste visual deve rodar nele.
- Revelação de texto antes da fonte carregar. Pré-condição de `TextReveal`.
- Tremor sem semente estável entre quadros faz o traço "pular". Usar sempre `frame` e `boilEvery`.

## 9. Ordem e dependências

1. `inkGeometry` (2).
2. `InkStroke` (3.1).
3. Atraso de cor no `DrawPath` (3.2), independente.
4. `PenTip` (3.3), usa `samplePath`.
5. `Erase` (3.4) e `TextReveal` (3.7), usam `SoftMask`.
6. `FillLevel` (3.5) e `LabelBox` (3.6), usam `TextReveal`.
7. `StackBuild` (3.8).
8. `StickLimbs` (3.9), depois da decisão sobre o corpo.
9. `Board` (3.10) no template, com ADR do contrato.
10. Migração do protótipo: trocar `tinta.ts` e `componentes.tsx` pelas peças do kit. Vídeo-régua em cada passo.

## 10. Decisões técnicas a confirmar

1. **Taper por polígono ou por máscara?** Recomendo polígono: é o único jeito de afinar a espessura de verdade.
2. **Tremor pelo `wobblePoint` do kit, e não o meu.** Recomendo. O visual muda um pouco; é preciso aceitar.
3. **`clipPath` do SVG no `FillLevel`.** Recomendo.
4. **Um `<svg>` por caixa.** Recomendo.
5. **`Board` no template na primeira versão.** Recomendo, até a ADR.
6. **Forma da ponta (`PenTip`).** Recomendo `dot`; não há mão nem forma reconhecível de caneta.
