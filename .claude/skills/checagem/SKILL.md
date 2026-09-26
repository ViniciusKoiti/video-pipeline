---
name: checagem
description: |
  Confere, sem editar nada, se fichas e roteiro de um episódio dizem só o que os trechos citados das
  fontes dizem: números, datas, nomes, relações, causas, superlativos. Use depois do roteiro e depois de
  qualquer reescrita, antes do gate 2 (ADR 009).
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
   - texto na tela (`number`, `stamp`, `lower_third`, `quote`, `chart`, `timeline`, `family_tree`)
     igual à ficha, e `quote` literal da fonte.
3. **Pessoas vivas:** nada de vida privada; só fato público com documento.

## Relatório

Uma linha por problema, do mais grave ao menos grave (exemplo só de formato):

```
DIVERGE     S03 "No ano seguinte, o genro já dirigia a empresa" — source-02#E9 diz "em 1927"; F08 diz 1926
SEM SUPORTE S04 "por isso decidiu entrar no cimento" — nenhuma ficha afirma a causa
EXAGERO     S01 plano number "47 anos no comando" — F02 dá 1926–1973 como diretor, não "no comando"
TELA        S02 lower_third "comprador da fábrica" — F01 diz "adquiriu o controle"
```

Para cada linha, sugira a correção mínima (trocar a palavra, tirar a causa, citar outra ficha). No fim,
diga quantas frases e planos conferiu e quantos passaram. Não reescreva os arquivos.
