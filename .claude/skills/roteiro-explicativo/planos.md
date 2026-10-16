# Planos da ADR 011: formato e exemplo

Exemplos só de formato, com dados neutros: nenhum valor aqui é fato. No roteiro, as `claims` levam os
`source_ids` e `excerpt_ids` das fichas usadas. Os exemplos passam no schema (`tests/test_editorial_shots.py`).

## `compare`: dois valores

```json
{"kind": "compare", "anchor": "A receita passou", "mode": "before_after", "emphasis": "right",
 "left": {"value": "R$ 12,5 bi", "label": "receita em 2010"},
 "right": {"value": "R$ 47,6 bi", "label": "receita em 2020"},
 "claims": [{"text": "receita 2010 e 2020", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E4"]}]}
```

- `value` como a ficha escreve. `side` mostra os dois lado a lado; `before_after` liga os dois com uma seta.
- `scale` desenha dois quadrados de área proporcional e pede a mesma unidade nos dois lados.

## `network`: quem se liga a quem

```json
{"kind": "network", "anchor": "A Empresa A", "root": "empresa-a", "layout": "radial",
 "nodes": [{"id": "empresa-a", "label": "Empresa A", "kind": "company"},
           {"id": "banco-b", "label": "Banco B", "kind": "bank"},
           {"id": "governo", "label": "Governo federal", "kind": "government"}],
 "edges": [{"from": "banco-b", "to": "empresa-a", "label": "empresta a", "value": "R$ 10 mi", "flow": true,
            "claims": [{"text": "empréstimo", "source_ids": ["source-02"], "excerpt_ids": ["source-02#E7"]}]},
           {"from": "governo", "to": "banco-b", "label": "avaliza", "style": "dashed",
            "claims": [{"text": "aval", "source_ids": ["source-03"], "excerpt_ids": ["source-03#E2"]}]}],
 "steps": [{"anchor": "no Banco B", "nodes": ["banco-b"]},
           {"anchor": "o governo", "nodes": ["governo"]},
           {"anchor": "No fim", "highlight": ["empresa-a", "banco-b", "governo"]}],
 "claims": [{"text": "atores da rede", "source_ids": ["source-02"], "excerpt_ids": ["source-02#E7"]}]}
```

- A raiz abre o plano; cada outro nó entra num passo. `steps[].anchor` é literal na narração, depois da
  âncora do plano e antes do plano seguinte: a rede cresce no ritmo da fala.
- `kind` do nó: `person`, `family`, `company`, `bank`, `government` ou `other` (o ícone sai daí).
- `flow: true` quando dinheiro corre de `from` para `to`; `style: "dashed"` para relação indireta.
- `layout: "layered"` para cadeia de controle, de cima para baixo.

## `chart`: linha e participação

```json
{"kind": "chart", "anchor": "A receita subiu", "type": "line", "title": "Receita da Empresa A",
 "unit": "R$ bi", "highlight": "2016",
 "points": [{"label": "2014", "value": 4.6}, {"label": "2016", "value": 3.4}, {"label": "2020", "value": 5.6}],
 "claims": [{"text": "série de receita", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E9"]}]}
```

```json
{"kind": "chart", "anchor": "Mais da metade", "type": "share", "title": "Capital da Empresa A",
 "unit": "% do ativo", "highlight": "de terceiros",
 "points": [{"label": "de terceiros", "value": 61}, {"label": "próprio", "value": 39}],
 "claims": [{"text": "composição do capital", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E10"]}]}
```

- `y_from_zero` fica `true`; desligue quando a variação pequena for o ponto e a narração disser a escala.
- A unidade longa ("contos de réis") vai para o subtítulo do gráfico sozinha.

## `quote` como documento

```json
{"kind": "quote", "anchor": "O relatório diz", "style": "document", "variant": "report",
 "text": "A receita cresceu pelo terceiro ano seguido [...] puxada pelas vendas ao Banco B.",
 "attribution": "Relatório anual da Empresa A",
 "document": {"title": "Relatório anual", "issuer": "Empresa A", "date": "2020"},
 "claims": [{"text": "trecho do relatório", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E5"]}]}
```

- `text` literal do trecho citado, com "[...]" nos cortes, até ~200 caracteres; o cabeçalho vem da fonte.
- `variant`: `report` (relatório), `newspaper` (jornal) ou `letter` (carta).

## `map` no mundo

```json
{"kind": "map", "anchor": "O dinheiro veio", "scope": "world",
 "places": [{"name": "Cidade A", "lat": 51.5, "lon": -0.13}, {"name": "Cidade B", "lat": -23.5, "lon": -47.46}],
 "routes": [{"from": "Cidade A", "to": "Cidade B"}], "highlight": ["GBR", "BRA"],
 "claims": [{"text": "origem do empréstimo", "source_ids": ["source-02"], "excerpt_ids": ["source-02#E3"]}]}
```

- Códigos: país em ISO 3166-1 alfa-3 ("BRA"), estado em ISO 3166-2 ("BR-SP"); o `vp check` confere.
- `highlight` e `routes` afirmam algo, por isso levam `claims`.

## `timeline` em escala real

```json
{"kind": "timeline", "anchor": "Em setenta anos",
 "events": [{"date": "anos 1950", "label": "Primeira filial", "when": "1950"},
            {"date": "12 mar. 2020", "label": "Fusão com o Banco B", "when": "2020-03-12"}],
 "claims": [{"text": "datas da empresa", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E2"]}]}
```

- `date` é o texto na tela; `when` é a posição na linha, com o mesmo ano escrito em `date`.

## `keyword`: frase-chave

```json
{"kind": "keyword", "anchor": "parada havia dois anos", "text": "parada havia dois anos", "highlight": "dois anos"}
```

- Palavras copiadas da narração, com o mesmo sentido da frase inteira: quem disse, a negação e a ressalva
  ficam dentro do trecho.

# Planos dos Reels (ADR 028): só no vertical

## `hook`: o gancho no primeiro quadro

```json
{"kind": "hook", "anchor": "Você está cobrando", "text": "Você está cobrando o docinho errado.", "highlight": "errado"}
```

- Só no primeiro plano do vídeo, e um só. `text` copiado da narração da primeira cena, até 14 palavras.
- Número, data ou nome no `text` leva `claims`, como qualquer coisa na tela.

## `calculation`: a conta dita inteira

```json
{"kind": "calculation", "anchor": "A embalagem custa",
 "terms": [{"text": "R$ 18,44", "label": "a embalagem", "anchor": "dezoito e quarenta e quatro"},
           {"op": "÷", "text": "395 g", "label": "o peso", "anchor": "trezentos e noventa e cinco"},
           {"op": "×", "text": "195 g", "label": "a receita", "anchor": "cento e noventa e cinco"}],
 "result": {"text": "R$ 9,10", "label": "custo na receita", "anchor": "dá nove e dez"},
 "claims": [{"text": "18,44 ÷ 395 × 195 = R$ 9,10", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E3"]}]}
```

- Só em vídeo que explica (ADR 020). Cada termo e o resultado entram quando a narração os diz: `anchor` literal,
  em ordem, dentro do trecho do plano; só o primeiro termo pode ficar sem, e entra com o plano.
- `op` em todo termo a partir do segundo: `+`, `−`, `×` ou `÷`. A tela não calcula: o `vp check` refaz a conta
  (× e ÷ antes de + e −; "20%" vale 0,2) e recusa o resultado que não bate nas casas escritas.
- Substitui o `number` com a conta no rótulo; o `number` fica para o valor que a ficha traz pronto.

## `receipt`: nota ou orçamento

```json
{"kind": "receipt", "anchor": "No pote entram", "title": "Bolo de pote",
 "items": [{"label": "Farinha", "value": "R$ 2,10", "detail": "200 g"},
           {"label": "Manteiga", "value": "R$ 4,80", "anchor": "manteiga"}],
 "total": {"value": "R$ 6,90", "anchor": "no total"},
 "claims": [{"text": "2,10 + 4,80 = 6,90", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E5"]}]}
```

- Uma linha por item, todas na mesma moeda; a primeira pode entrar com o plano, as outras na sua `anchor`.
- O `total` é a soma das linhas: a claim escreve a soma inteira, a narração diz o total e o `vp check` refaz a
  conta (ADR 028, decisão 2). Sem `total`, a nota é só a lista.

## `end_card`: o cartão final

```json
{"kind": "end_card", "anchor": "Salva pra conferir", "variant": "save", "text": "Salve para fazer a sua conta",
 "sub": "Parte 3: o preço final"}
```

- Só no último plano do vídeo. `variant`: `follow` no topo, `save` no meio (ADR 026); `next` quando a série
  continua (`series` no roteiro, com uma parte depois desta). No fundo ainda não há cartão final.
- A `cta` do `funnel` é dita no trecho do cartão. `series: {"name": ..., "part": 2, "total": 3}` no `scenes.json`
  desenha o selo "Parte 2 de 3".
