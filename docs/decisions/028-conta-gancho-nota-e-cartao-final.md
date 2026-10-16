# 028 — Planos de conta, gancho, nota e cartão final

- **Status:** proposta, aguardando o dono (2026-10-16). Nada do contrato está implementado; onde diz **decisão
  aberta**, o agente não decide.
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

## Proposta

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

## Decisões abertas (do dono)

1. **Fade da primeira cena:** tirar sempre (proposta) ou só quando houver `hook`. Tirar sempre muda o
   `template_hash` e o primeiro quadro de todo vídeo renderizado de novo.
2. **Total da nota:** a soma dos itens pode ir à tela sem a narração dizer cada parcela? Proposta: pode, se a
   claim escreve a soma inteira ("2,10 + 4,80 = 6,90"), o `vp check` refaz a conta e a narração diz o total. É
   emenda à ADR 020, que hoje exige a conta inteira dita.
3. **`receipt` e a spec `value-table`:** a proposta é a nota servir ao dinheiro (um valor por linha, mesma moeda)
   e a tabela continuar como rascunho para unidades misturadas. Ou a nota substitui a tabela.
4. **Chamada do fundo:** variante nova no kit (`comment`, com a palavra) antes do primeiro vídeo de fundo, ou o
   cartão final fica fora do fundo por enquanto.
5. **Ordem:** a proposta é implementar `hook`, `calculation` e `end_card` primeiro, para o
   `confeitaria-erro-2-pt` nascer neles (gate 1 pendente), e o `receipt` depois, para o `prestador-hora-pt`.

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

## Consequências, se aceita

- `app/pipeline/schemas.py` (`CalculationShot`, `HookShot`, `ReceiptShot`, `EndCardShot`, `Series`; grupos de
  planos), `app/pipeline/check.py` (aritmética da conta e da nota, posição do gancho e do cartão final, texto na
  narração, cartão final e `cta`), `app/pipeline/shots.py` (âncoras dos termos e itens), adaptador
  (`app/render/remotion.py`), template (`video/src/types.ts`, `ShotView.tsx`, `Editorial.tsx`, `Scene.tsx`).
- Skills `roteiro-explicativo` e `checagem`, CLAUDE.md §6 e as ADRs 011, 020 e 026 com a emenda datada.
- Vídeo-régua com a versão nova e a sonda de CPU antes do render.
