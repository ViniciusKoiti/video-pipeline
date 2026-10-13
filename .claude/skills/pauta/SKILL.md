---
name: pauta
description: |
  Escreve a pauta de um episódio curto (Reel) antes de baixar fontes: público, tema concreto, forma e o que
  as fontes precisam responder, a partir do resumo do reels-radar do nicho. Use no começo de um episódio,
  depois de `radar_resumo.py` e antes das fontes (ADR 018).
argument-hint: "<episode-id>"
---

# Pauta: o resumo do radar → o que vale pesquisar

A pauta decide **o que** o vídeo vai procurar nas fontes e **com que forma** ele sai. Ela não afirma nada: é
uma lista de perguntas e escolhas, que o dono aprova antes de qualquer download (gate de tema, §2.5).

## Entrada

- `data/episodes/<id>/radar-brief.json`: cópia do resumo do nicho (`script_brief.v1`), trazida por
  `scripts/provisorio/radar_resumo.py <id> <nicho>`. Sem o arquivo, pare e diga que falta: não escreva a pauta
  de memória.
- O que o dono disse sobre o tema e o ângulo.

O resumo é observação de amostra pequena (`analysed` diz quantos Reels), nunca fonte de fato. Leia
`how_to_read` e `caveats` antes do resto.

## Saída: `data/episodes/<id>/pauta.md`

1. **Nicho e base.** Nome do nicho, quantos Reels, data do resumo e a medida usada. Se o resumo tem mais de 45
   dias ou menos de 30 Reels, diga isso na primeira linha.
2. **Público.** Quem assiste, nas palavras do dono. Não deduza do resumo.
3. **Objetivo (ADR 019).** O que o dono quer que o vídeo faça: `noticiar`, `explicar`, `opinar`, ou mais de
   um, na ordem. Mais a promessa em uma frase. Se ele não disse, este item fica como pergunta ao dono, com as
   opções; não escolha por ele. Para `opinar`, a tese é dele e vem escrita por ele.
4. **Tema concreto.** Dos `themes` com `strength: "pattern"`, quais têm a ver com o ângulo do dono. Para cada
   um, a pergunta que as fontes precisam responder para o tema poder entrar. Tema `avoid` ou `hint` vai numa
   linha à parte, como hipótese.
5. **Forma.** Uma linha por padrão de `guidance` (o que usar, o que evitar, com `n` e `chance`), os cortes de
   `thresholds` e o perfil de `top` (duração e tamanho da abertura dos melhores). Separe o que o roteiro
   controla (abertura, duração, título na tela, legenda) do que depende do vídeo (pessoa falando para a câmera).
6. **O que as fontes precisam responder.** De três a seis perguntas neutras, sem resposta embutida. Marque a
   que sustenta falar com quem assiste: se nenhuma fonte responder a ela, o vídeo não pode afirmar nada sobre
   o espectador.
7. **Critério de parada.** O que precisa aparecer nas fichas para a promessa do item 3 se sustentar. Sem isso depois do
   fichamento, a pauta volta ao dono antes do roteiro.
8. **O que o resumo não diz.** O que está em `no_basis`, e o que só uma coleta nova responderia. Coleta que
   gasta crédito é decisão do dono: não a proponha como passo automático.

## Regras

- Nenhum fato sobre a pessoa, a empresa ou o assunto: só perguntas. Um fato escrito na pauta vira roteiro, e o
  `vp check` não pega (§14).
- Não copie frase, título nem imagem dos Reels citados em `evidence` e `top.watch`; cite só o id, para o dono
  assistir.
- Fale em "associado a", nunca em "causa".
- A pauta não escolhe fontes; ela diz o que elas precisam responder.

## Fechamento

Entregue a pauta ao dono com as dúvidas agrupadas. Só depois do ok dele vêm as fontes, o `vp excerpts` e a
skill `fichamento`.
