# 028 — Planos de conta, gancho, nota e cartão final

- **Status:** aceito pelo dono em 2026-10-16, como proposto (decisões abaixo); implementado no mesmo dia.
- **Data:** 2026-10-16
- **Etapa do roadmap:** roteiro (#28), checagem (#31) e template do `explainer`
- **Relaciona-se com:** ADR 008 (planos), ADR 011 (planos editoriais; decisões 5 e 7), ADR 014 (perfil
  vertical), ADR 020 (conta feita na tela), ADR 022 (entrega da fala), ADR 026 (estágio do funil), ADR 027
  (motion-kit por tarball). Issues #124 (gancho e CTA), #125 (lista), #127 (comparações). Specs irmãs em
  `docs/specs/` (`value-table`, `reveal-list`).

## Contexto

Os três primeiros reels da série da confeitaria contornaram o que o template não tinha:

- **A conta vira rótulo.** Em `confeitaria-ingrediente-pt`, S03 e S04 mostram um `number` com o rótulo
  "dividido por 395 g…": a conta que a ADR 020 manda dizer inteira aparece como texto pequeno embaixo do
  resultado, e os insumos não aparecem.
- **O gancho chega tarde.** Todo vídeo do `explainer` começa com o quadro preto, porque cada cena entra com fade
  de 0,3 s (`fadeFrames` em `video/src/Scene.tsx`, `fade_s` em `app/render/remotion.py`). No gate 4 de
  `confeitaria-erro-pt` o gancho ficou legível perto dos 3 s; o Reel decide nos 2 primeiros.
- **Orçamento sem lugar.** A série 1 (parte 3) e a série 2 (custos fixos do prestador) listam itens com valor e
  um total. O `compare` tem dois lados; o `chart` supõe uma unidade e não tem coluna de texto.
- **A chamada final é só voz.** A ADR 026 exige que a `cta` seja dita; na tela ela não aparece, nem a parte da
  série.

O motion-kit 0.4.0 (ADR 027) trouxe as peças: `Equation`, `HookCard`, `Receipt`, `EndCta` e `SeriesBadge`, com
área segura do Reels e modo capa (`SettledEntrances`). Falta o contrato que as liga ao roteiro.

## Decisão

Quatro planos novos no `scenes.json` e no `episode.json`, com o espelho em `video/src/types.ts`. Todos entram
primeiro no vertical (`PORTRAIT_SHOT_KINDS`); no 16:9, só depois do vídeo-régua.

### 1. `calculation` → `Equation`

```json
{"kind": "calculation", "anchor": "dezoito e quarenta e quatro, dividido por trezentos e noventa e cinco",
 "terms": [
   {"text": "R$ 18,44", "label": "a embalagem", "anchor": "dezoito e quarenta e quatro"},
   {"op": "÷", "text": "395 g", "label": "o peso", "anchor": "trezentos e noventa e cinco"},
   {"op": "×", "text": "195 g", "label": "a receita", "anchor": "cento e noventa e cinco"}],
 "result": {"text": "R$ 9,10", "label": "custo na receita"},
 "claims": [{"text": "18,44 ÷ 395 × 195 = R$ 9,10", "source_ids": ["..."]}]}
```

- Plano de tela cheia (`GRAPHIC_SHOT_KINDS`), só em vídeo de objetivo `explicar` (ADR 020, item 3).
- Cada termo entra na sua âncora, como os passos da rede (`step_positions` generalizado).
- A tela continua sem calcular: os textos vêm prontos do roteiro. O `vp check` refaz a aritmética e recusa
  resultado errado, arredondado como se fala. É o candidato da ADR 020 (item 4) saindo do papel.
- Substitui o `number` com a conta no rótulo. O `number` continua para o número que vem pronto de uma ficha.

### 2. `hook` → `HookCard`, e a primeira cena sem fade de entrada

```json
{"kind": "hook", "anchor": "você está cobrando o docinho errado",
 "text": "você está cobrando o docinho errado", "highlight": "errado"}
```

- Só pode ser o primeiro plano da primeira cena; no máximo um por vídeo.
- O `text` aparece na narração, literal, como o `keyword`: a tela diz o que a voz diz, e quem assiste sem som lê
  o gancho.
- Número, data ou nome no `text` pede `claims`, como qualquer coisa na tela (§2.2).
- O plano entra assentado no quadro 0 (modo capa do kit). **A primeira cena perde o fade de entrada** (o de saída
  continua): o primeiro quadro deixa de ser preto em todo vídeo, com ou sem `hook`.
- O `delivery: "hook"` da ADR 022 continua sendo da voz; os dois andam juntos, mas um não exige o outro.

### 3. `receipt` → `Receipt`

```json
{"kind": "receipt", "anchor": "farinha, manteiga, ovos e a embalagem", "title": "Bolo de pote",
 "items": [{"label": "Farinha", "value": "R$ 2,10", "anchor": "farinha"},
           {"label": "Manteiga", "value": "R$ 4,80", "anchor": "manteiga"}],
 "total": {"label": "Custo", "value": "R$ 6,90"},
 "claims": [...]}
```

- Tela cheia, itens no ritmo da narração (como a lista da spec `reveal-list`).
- Cada item com valor é afirmação e aponta para a sua ficha.
- O `total`: ver a decisão aberta 2.

### 4. `end_card` → `EndCta` com `SeriesBadge`

```json
{"kind": "end_card", "anchor": "salva esse vídeo", "variant": "save", "text": "Salve para fazer a conta",
 "sub": "Parte 2: o docinho"}
```

- Só no último plano da última cena.
- A `variant` segue o estágio do funil (ADR 026): `topo` → `follow`, `meio` → `save`. No `fundo` o kit ainda não
  tem a variante (comentar a palavra, link na bio): ver a decisão aberta 4.
- O `anchor` cai na `cta` dita. O `vp check` avisa quando o plano e a `cta` do `funnel` não batem.
- **A série vai ao `episode.json`.** O `scenes.json` ganha `series: {name, part, total}` ao lado de `funnel`, e a
  montagem copia para o `episode.json`, que desenha o selo "Parte 2 de 3". É emenda à ADR 026 ("o `episode.json`
  não muda"): o estágio continua só no roteiro.

## Decisões (do dono, 2026-10-16: "como você propôs")

1. **Fade da primeira cena: sai sempre**, com ou sem `hook`. Muda o `template_hash` e o primeiro quadro de todo
   vídeo renderizado de novo.
2. **Total da nota:** a soma dos itens vai à tela sem a narração dizer cada parcela, quando a claim escreve a soma
   inteira ("2,10 + 4,80 = 6,90"), o `vp check` refaz a conta e a narração diz o total. Emenda à ADR 020.
3. **`receipt` serve ao dinheiro** (um valor por linha, mesma moeda); a spec `value-table` continua rascunho para
   unidades misturadas.
4. **Chamada do fundo:** a proposta não escolheu um lado. Ficou o reversível: o contrato recusa o cartão final num
   roteiro de fundo até o kit ganhar a variante (`comment`, com a palavra). Não há vídeo de fundo ainda.
5. **Ordem:** os quatro planos entraram juntos, para o `confeitaria-erro-2-pt` (gate 1 pendente) nascer neles e o
   `prestador-hora-pt` ter a nota.

## O que não muda

- Roteiros aprovados ficam como estão (§2.6): os reels 1 e 2, agendados para 16 e 18/10, e o reel 3 não ganham os
  planos novos por esta ADR.
- O que a tela mostra continua escrito pelo roteirista e refeito pelo verificador; o template não calcula
  (ADR 011, decisão 7).

## Fora desta ADR (próximas)

- Comparação em modo "revelação" (antes → depois na mesma tela) e tela dividida (#127).
- Trecho do B-roll (`FootageBackground` com início e fim) no plano `broll`.
- Trilha sonora (#81).
- `locale` no `BarChart` do kit, que já existe na 0.4.0. A ligação no template tira o limite temporário do
  `chart` em inglês (ADR 011, emenda "número por idioma", item 5), num PR à parte.

## Implementação (2026-10-16)

- **Contrato** (`app/pipeline/schemas.py`): `CalculationShot`, `ReceiptShot`, `HookShot`, `EndCardShot`,
  `Series`, `REELS_SHOT_KINDS` e `reels_shot_problems` (só no vertical; gancho só no primeiro plano, cartão final
  só no último; `next` pede a série com parte seguinte; fundo sem cartão final). `step_anchors` e `step_positions`
  valem para a rede, a conta e a nota: só a primeira parte pode ficar sem âncora, e entra com o plano.
  `EpisodeShot.steps_ms` traz um tempo por parte; `EpisodeManifest.series` leva o selo.
- **`vp check`** (`app/pipeline/check.py`): `arithmetic_errors` refaz a conta (× e ÷ antes de + e −, "20%" vale
  0,2) e a soma da nota, e recusa unidades misturadas; conta e total só em vídeo que explica; o cartão final é
  conferido contra o funil (`END_CARD_VARIANTS` e a `cta` dita durante ele).
- **Montagem e adaptador:** `series` vai do roteiro ao `episode.json` (`montar_episodio.py`) e às props do cartão
  final; a primeira cena leva `fadeIn: false` (`app/render/remotion.py`).
- **Template** (`video/src`): `CalculationShot`, `ReceiptShot`, `HookShot` e `EndCardShot` em `Editorial.tsx`, na
  área segura `vertical`, com a fonte em cima e a legenda embaixo livres; sem câmera própria do template
  (`Scene.tsx`); "Total" e "Parte 2 de 3" nos dois idiomas (`labels.ts`).
- **Skills** `roteiro-explicativo` (tabela e exemplos em `planos.md`) e `checagem`; CLAUDE.md §6; emendas datadas
  nas ADRs 011, 020 e 026. Testes em `tests/test_reels_shots.py`.
- **Antes do primeiro vídeo:** vídeo-régua com a versão nova do template e a sonda de CPU antes do render.
