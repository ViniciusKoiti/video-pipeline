# Componentes que o motion-kit deveria ter para cobrir a camada de Infographic

- **Consulta:** 2026-10-07. **Origem:** o conselho de estilos achou que Infographic + Swiss style (o preset `editorial`) serve 9 das 10 verticais (`docs/pesquisa/estilos-por-vertical-2026-10.md`); o dono perguntou que componentes faltam para cobrir melhor essa camada.
- **Método:** leitura do kit (`~/projetos/motion-kit`, `a2dcca3`), do template e do schema, cruzada com os formatos de Reel já mapeados nas pesquisas de nichos. **Sem conselho de modelos e sem renders.** Os esforços são relativos e **[I]**; as contagens de "formatos que destrava" são minha leitura das tabelas de formato **[I]**.
- **Estado:** análise. Nada foi implementado. **Specs: item 1 (`ValueTable`) em `docs/specs/value-table.md`; item 2 (`LimitMeter`) em `docs/specs/limit-meter.md`; item 3 (`RevealList`) em `docs/specs/reveal-list.md`; item 5 (waffle) em `docs/specs/waffle-chart.md`.**

## 1. O que a camada cobre hoje [F]

| Peça | O que faz | No template |
|---|---|---|
| `BarChart` | barras verticais ou horizontais, contagem até o valor | plano `chart` (`bar`, `bar_horizontal`) |
| `LineChart` | uma ou várias séries, eixos que se desenham, `annotate` | `chart` (`line`; rótulos precisam ser anos ou datas ISO) |
| `ShareChart` | partes de um todo: barra de 100% ou rosca, com fatia `rest` | `chart` (`share`, só `bar100`) |
| `ValueCompare` | dois valores lado a lado, antes e depois, ou em escala; só número (usa o `Odometer`) | plano `compare` (**exatamente dois lados**) |
| `YearTimeline` | cronologia com câmera | `timeline`, **fora do retrato** (ADR 014) |
| `Odometer`, `DateStamp`, `SourceTag`, `LowerThird`, `Highlighter`, `KineticHeadline` | número que rola, selo, fonte, tarja, marca-texto, frase animada | planos `number`, `stamp`, `lower_third`, `keyword` |
| `Gauge`, `Pipeline`, `VersusSplit`, `PayoffReveal`, `CtaScene`, `Marker`, `GeoMap` | medidor radial (aceita `zones`), esteira, A × B com vencedor, valor antigo → novo, CTA, anotação a caneta, mapa | **sem plano** (`GeoMap` só em paisagem) |

O `ChartShot` do schema tem `type`, `highlight`, `y_from_zero` e `rest`; não tem coluna de texto, limite, anotação nem unidades misturadas. **Não existe no kit** nenhum componente de tabela, lista, calendário, cascata, waffle, medidor de limite linear, sparkline ou callout (busca por nome de arquivo).

## 2. O que falta, em ordem de prioridade

| # | Componente novo | O que faz | Formatos da pesquisa que destrava [I] | Reaproveita | Contrato | Esforço |
|---|---|---|---|---|---|---|
| 1 | **`ValueTable`** | linhas `rótulo | valor | nota` com **unidades e texto misturados**, revelação linha a linha, destaque de uma linha, barra opcional quando a unidade é a mesma | DAS por atividade (3 valores); pisos de renda por país; planos de software; taxas do Etsy (US$ 0,20, 6,5%, 15%); comissão por categoria; metas de proteína; ≈7 | `SourceTag`, `useInOut`, tokens de entrada | plano novo `table` (ADR; entra na lista do retrato) | M |
| 2 | **`LimitMeter`** | barra linear com **limites e zonas rotulados** e marcador opcional; sem "faltam X" | limite do MEI (R$ 81 mil, R$ 6.750/mês, +20% = R$ 97.200); US$ 20.000 e 200 transações do 1099-K; açúcar por refeição; US$ 1.000 dos trimestrais; ≈4 | ideia do `Gauge` (zonas), `BarChart` | `chart` com `type: "limit"` (ADR), pontos = limites, `highlight` = marcador | M |
| 3 | **`RevealList`** | lista numerada que **acumula** quando o item é dito; título; itens anteriores já assentados | preço em quatro partes; "5 jeitos" (já existe o episódio `votorantim-5-jeitos`); quem pode te aconselhar; passo a passo; ≈5 | convenção `steps[].at` da rede; `HostWindow` (`at=-60`) | plano novo `list` (ADR); entra em `LONG_KINDS` por causa do teto de 6 s | M |
| 4 | **`DeadlineBoard`** | linhas `data | evento`, com visual de painel (split-flap) opcional | DASN (último dia de maio); quatro prazos trimestrais; prazos do MTD; rodadas do Express Entry; ≈4 | `ValueTable` com coluna de data | variante de `table` (sem plano a mais) | S depois do 1 |
| 5 | **`ShareChart` em waffle** | grade de 100 quadrados com a fração preenchida: "63 em cada 100" | 63% cobririam US$ 400; 60,2% usam suplemento; 17% a 20% das empresas usam IA; 31% economizaram tempo; ≈4 | `ShareChart` (mesma entrada) | campo opcional `variant` no `chart` (ADR; spec em `docs/specs/waffle-chart.md`) | S |
| 6 | **`Waterfall`** (cascata) | preço → taxas → o que sobra, passo a passo | onde vai cada US$ 100 de uma venda; faturamento não é dinheiro no bolso; ≈3 | `BarChart`, `ShareChart` | exige **política do número derivado** (ver §3); ADR | L |
| 7 | **`ChartCallout`** | círculo ou sublinhado a caneta sobre a barra ou o ponto de `highlight`, com 2 ou 3 palavras | qualquer gráfico com `highlight`; "tempero, 1 a 2 por vídeo" | `Marker` (existe, o template não usa) | **nenhum**: usa o `highlight` que já existe | M |
| 8 | **`VerdictCard`** | afirmação → veredito (mito ou fato) com a fonte | mito × fato do crédito; mitos de nutrição; ≈3 | `VersusSplit` | plano novo ou `compare` com texto (ADR) | M |
| 9 | **`CommentCta`** | cartão final "comente PALAVRA" e o que a pessoa recebe | o funil de isca do plano de 14 dias (todas as verticais) | `CtaScene` (hoje é uma pergunta A × B) | só template | S |
| 10 | **`LocatorMap`** | mapa pequeno com um ou dois países acesos, em retrato | imigração (país do visto); placar Brasil × país | `GeoMap` | ADR 014 hoje exclui o mapa do retrato | M |

**Fundação, antes dos itens acima:** tokens de movimento (`cut`, `pop`, `rise`, do `docs/guia-animacao-de-texto.md`) e tokens de gráfico (espessura de traço, tamanho de rótulo e de eixo) no `MotionTheme`. Sem isso, os componentes novos repetem as ~10 molas em linha do kit, e nenhum outro estilo consegue reaproveitá-los.

**Não adicionar agora:** Sankey, treemap, radar, dispersão e gráficos 3D (nenhum formato mapeado precisa deles); o `Gauge` neon como padrão (é o visual de "hook analógica", destoa do `editorial`).

## 3. Regras que valem para todos [F]

- **A tela não calcula (ADR 011, decisão 7):** cada valor, limite e item chega pronto, de uma ficha com fonte; o componente não soma, não tira razão e não converte moeda. Como no `ValueCompare` (`showRatio` desligado), qualquer razão fica desligada por padrão.
- **Valor derivado:** o `ShareChart` com `rest` já calcula a fatia que sobra (`whole - sum`) e a ADR 011 lista `rest?`. Para a cascata (item 6) e o "quanto sobra" é preciso decidir se o líquido entra **como valor explícito de uma ficha** (recomendo) ou se o `vp check` o **valida** sem exibir cálculo. Exemplo hipotético ("quanto sobra de R$ 5 mil") continua exigindo uma ADR própria (`nichos-reels-animados.md` §2.5, item 2).
- **Retrato:** o perfil só aceita os 8 planos de `schemas.py` (l. 506 a 508). `table` e `list` entram nessa lista por ADR; `chart` com `limit` ou `look` só estende o que já está lá. Legenda, fonte, tarja e janela ficam na área segura (ADR 014); em retrato só os dois cantos de cima ficam livres para o apresentador.
- **Ritmo:** de 1,5 a 6 s por plano (`MIN_SHOT_MS`, `MAX_SHOT_MS`); tabela e lista pedem pelo menos 4 s para dar tempo de ler, como os outros planos de dado.
- **Um PR por frente:** o kit não tem contrato, então os componentes nascem lá, com demo em `examples/Root.tsx`, `typecheck`, build e `dist/`; o template só liga depois da ADR e do pin novo, com vídeo-régua e sonda de CPU.

## 4. Ordem de entrega proposta [I]

1. Tokens de movimento e de gráfico no kit (um PR).
2. `ValueTable` e `DeadlineBoard` (um PR no kit) e `LimitMeter` (outro).
3. **Uma ADR** que emenda a 011 e a 014: `table`, `list`, `chart` com `limit` e `look`, e a regra do número derivado.
4. Template: ligar `table`, `chart` estendido e `list`, com `vp check` e `text_fit` para cada um.
5. `ChartCallout`, `VerdictCard`, `CommentCta` e `LocatorMap`, conforme as verticais escolhidas.

## 5. O que ninguém verificou

- Esforço real de cada peça (as estimativas são relativas).
- Se `ValueTable` e `LimitMeter` ficam legíveis em 720×1280 com legenda queimada; nenhum quadro foi renderizado.
- Quantos formatos cada componente destrava de fato: a contagem é minha leitura das tabelas de formato.
- Se o dono quer uma `table` genérica ou prefere estender `compare` para três ou mais lados.
