---
name: checagem
description: |
  Confere, sem editar nada, se fichas e roteiro de um episódio dizem só o que os trechos citados das
  fontes dizem (números, datas, nomes, relações, causas, superlativos) e se os temas do roteiro se
  conectam e se consolidam na resposta. Use depois do roteiro e depois de qualquer reescrita, antes do
  gate 2 (ADR 009).
argument-hint: "<episode-id>"
---

# Checagem: cada afirmação contra o trecho citado

Você não escreveu estes arquivos e não vai editá-los. Suponha que há erro até conferir. O `vp check` já
garante que as citações existem; você confere se elas **sustentam** o que foi escrito.

## Entrada

`data/episodes/<id>/facts.json`, `scenes.json`, `outline.md` e `excerpts/*.md` (trechos numerados).

## O que conferir

1. **Fichas.** Para cada fato, leia o trecho inteiro de cada evidência, não só a citação. O `text` do
   fato diz a mesma coisa? Compare data, valor, unidade, quem fez, o verbo ("comprou", "arrendou",
   "assumiu o controle", "fundou").
2. **Roteiro, frase por frase.** Para cada frase da narração e cada plano:
   - números, datas, nomes e cargos batem com a ficha e o trecho?
   - relações de parentesco e de negócio estão certas (pai, genro, sócio, herdeiro)?
   - causa: "por isso", "então", "graças a" afirmam causa. A fonte afirma essa causa?
   - superlativos e pioneirismos ("o maior", "o primeiro", "o único"): a fonte diz isso?
   - intenção e sentimento ("queria", "temia", "apostou tudo"): a fonte diz isso?
   - frase que afirma fato sem `claims` → sem suporte.
   - texto na tela (`number`, `stamp`, `lower_third`, `quote`, `chart`, `timeline`, `family_tree`,
     `compare`, `network`, `map`, `keyword`) igual à ficha, e `quote` literal da fonte. Nos planos da
     ADR 011, também:
     - `compare`: os dois valores e rótulos estão nas fichas; razão, variação ou soma só se uma ficha trouxer;
       ou se for conta dita inteira na narração com insumos e regra em fichas (ADR 020): refaça a conta e confira
       o arredondamento e a unidade;
     - `calculation` e `receipt` (ADR 028): cada termo e cada linha estão numa ficha; o `vp check` já refaz a
       conta e a soma, então confira o que ele não vê: a regra da conta numa ficha, a unidade de cada termo e
       que a narração diz a conta inteira (na nota, o total);
     - `network`: cada aresta (quem, verbo, direção, valor) está no trecho das `claims` dela; tracejada só
       onde a fonte descreve relação indireta;
     - `quote` com `style: "document"`: título, emissor e data do cabeçalho correspondem à fonte;
     - `chart`: `highlight` no ponto que a narração comenta; em `type: "line"`, só anos das fichas;
     - `map`: país ou estado aceso e rota sustentados pelas `claims`;
     - `keyword`: lida sozinha, a frase mantém o sentido da narração inteira (quem disse, negação,
       ressalva); se o recorte muda o sentido → `EXAGERO`.
3. **Pessoas vivas:** nada de vida privada; só fato público com documento.
4. **Controvérsia e acusação:**
   - crime, fraude, cartel, intenção ou caráter afirmados diretamente pela narração → `SEM SUPORTE`,
     mesmo que o trecho traga uma acusação: o roteiro precisa dizer quem acusou ou decidiu, o quê e quando;
   - decisão citada sem o desfecho que o trecho dá (recurso, absolvição, acordo) → `DIVERGE`;
   - pergunta retórica ou insinuação que sugere algo que as fichas não dizem ("coincidência?") → `EXAGERO`.
5. **Ponte com o espectador:** frase em 2ª pessoa ("você usa", "você paga") precisa de ficha
   `impact_today` com escala e data; sem ela → `SEM SUPORTE`.
6. **Conexão e consolidação** (pedido do dono, 2026-10-21: roteiro que "joga um tema em cima do outro" não
   passa). Leia só a narração, em ordem, como quem ouve o vídeo uma vez:
   - cada autor, obra ou caso entra por uma frase que nasce do bloco anterior e sai voltando à obra
     principal ou à pergunta (`objective.question`); se quem ouve não sabe por que ele está ali → `CONEXÃO`;
   - cada bloco acrescenta uma parte da resposta à pergunta; bloco que não acrescenta ou repete outro →
     `CONSOLIDAÇÃO`;
   - os resumos e o fecho juntam as peças que de fato apareceram, com os mesmos nomes, e a tese decorre
     delas; peça anunciada que não volta, ou que volta sem ter sido apresentada → `CONSOLIDAÇÃO`;
   - a história principal anda na ordem que o roteiro promete; desvio sem aviso → `FIO`;
   - o que é plantado ("isso volta no fim") é pago; gancho sem pagamento → `GANCHO`.

   Correção só de forma (ponte, ordem, corte), nunca fato novo. No relatório, junte uma tabela curta dos
   blocos: cenas, parte da resposta que cada um acrescenta, ponte de entrada e ponte de saída.

## Relatório

Uma linha por problema, do mais grave ao menos grave (exemplo só de formato):

```
DIVERGE     S03 "No ano seguinte, o genro já dirigia a empresa" — source-02#E9 diz "em 1927"; F08 diz 1926
SEM SUPORTE S04 "por isso decidiu entrar no cimento" — nenhuma ficha afirma a causa
EXAGERO     S01 plano number "47 anos no comando" — F02 dá 1926–1973 como diretor, não "no comando"
TELA        S02 lower_third "comprador da fábrica" — F01 diz "adquiriu o controle"
TELA        S07 network aresta banco-b→empresa-a "empresta a" — source-02#E7 diz "avalizou o empréstimo"
CONEXÃO     S29 "Volta à taverna." — o bloco anterior não diz por que Raskólnikov volta; a ligação só vem na S31
```

Para cada linha, sugira a correção mínima (trocar a palavra, tirar a causa, citar outra ficha). No fim,
diga quantas frases e planos conferiu e quantos passaram. Não reescreva os arquivos.

## Parecer

Feche com este JSON, que a sessão principal grava com `vp checagem <id> parecer.json` e que o gate 2 exige
(sem ele, o dono só aprova com `--sem-checagem "motivo"`):

```json
{"verdict": "rejected", "problems": ["DIVERGE S03 \"No ano seguinte...\" — source-02#E9 diz \"em 1927\""]}
```

`approved` só sem nenhuma linha de problema; qualquer `DIVERGE`, `SEM SUPORTE`, `EXAGERO`, `TELA`,
`CONEXÃO`, `CONSOLIDAÇÃO`, `FIO` ou `GANCHO` é `rejected`, com as linhas do relatório em `problems`.
