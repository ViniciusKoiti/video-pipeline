# Recall do conferidor de texto, com defeitos injetados (Kira, 2026-11-07)

Continuação de `ocr-quadros-kira-2026-11-07.md`. Script: `scripts/bench/ocr_recall.py`. Saídas (JSON e cópias dos
quadros) em `data/cache/ocr-kira-voto-brasil/`, fora do Git. Base: os 23 quadros limpos do `final.mp4` do Kira
(render de 2026-10-20). Nenhum vídeo foi renderizado: só se editaram imagens PNG com o ffmpeg (`drawbox` e
`drawtext`, fonte Inter SemiBold, expansão de texto desligada).

## Defeitos injetados

- `corte`: a última palavra esperada do quadro é coberta com a cor do fundo, como texto cortado.
- `numero`: o primeiro dígito de um número de dois ou mais dígitos muda (57% vira 27%).
- `letra`: a primeira vogal de uma palavra longa muda (justiça vira jostiça).

Em cada quadro entra no máximo um defeito por tipo. Quadros que já alertavam limpos (os dois de comparação, com
números lidos errado) ficam de fora do recall.

## Resultado por limite de similaridade e cobertura

| Limite (similaridade = cobertura) | corte | número | letra | alarmes em quadros limpos |
|---|---|---|---|---|
| 0,8 (padrão atual) | 7/21 = 33% | 6/6 = 100% | 1/20 = 5% | 2/23 |
| 0,9 | 20/21 = 95% | 6/6 = 100% | 13/20 = 65% | 2/23 |
| 1,0 (qualquer palavra faltando conta) | 21/21 = 100% | 6/6 = 100% | 19/20 = 95% | 2/23 |

Os dois alarmes em quadros limpos são sempre os mesmos (os quadros 13 e 23, de comparação, com o 73% e o 55% lidos
errado). Com o limite 1,0 não surgiu nenhum alarme novo nos outros 21 quadros.

## O que a medição mostra

- **O padrão atual deixa passar a maioria dos defeitos de texto.** Com 80%, uma palavra sumida numa frase de 9 palavras
  não derruba a cobertura abaixo do limite, e uma letra trocada numa palavra longa ainda é tida como lida.
- **Número foi pego em todos os casos com qualquer limite.** Um dígito trocado sempre cai como número divergente.
- **Com 1,0, o único erro perdido foi um caso de mascaramento.** A letra trocada em "Chapman" (rótulo de S08) passou
  porque o mesmo nome aparece no rodapé "Fonte: Chapman". A leitura achou o nome no rodapé e deu o texto como
  completo. Um nome repetido na tela esconde erro no outro lugar.

## Limites desta medição

- Um vídeo, 23 quadros. Não diz como o limite se comporta em texto mais denso ou em outros formatos (Reels, Shorts).
- Os defeitos são simulados: a caixa de fundo sobre a palavra e a fonte Inter SemiBold não são idênticas ao render.
- Os quadros são de 1080p. Vídeo baixado a 360p (padrão do `baixar.py` de análise de formato) tem texto menor e
  deve render menos. Não medido.

## Proposta (não aprovada)

- Trocar o padrão de `ocr_quadros.py` para 1,0 e rodar a mesma medição em um segundo episódio com texto mais denso
  (por exemplo, `death-note-fins-meios` ou `montaigne-desapego`), medindo alarmes em quadros limpos e recall.
- Só depois disso, decidir se o conferidor entra na prévia antes do gate 4, e com que tratamento para os erros de
  número em cartões de comparação.
