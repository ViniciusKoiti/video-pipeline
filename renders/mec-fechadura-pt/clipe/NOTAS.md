# Clipe do corte principal (S04–S11), traço limpo — notas de 2026-11-09

Código: `video/src/previews/mec-fechadura-pt/` (`index.tsx`, `geometria.ts`, `linhaDoTempo.ts`, `tempos.json`, `check.mjs`). Composição `FechaduraClipe`, 1280×720 a 30 fps, 2167 frames (72,2 s),
igual à soma da voz de S04 a S11 (`voice/leveled/*.wav`). Sem commit. **Só quadros foram renderizados; nenhum vídeo.**

Quadros: `q-<frame>.png` (13) e `folha-contato.png`. Frames escolhidos: 60, 200 (S04), 403 (S05), 749 (S06), 854 (S07), 1202 (S08), 1560 e 1649 (S09), 1700, 1745 e 1790 (S10), 1905 (S11), 2166 (fim).

## O que foi conferido por código (`node ... check.mjs`)
Geometria (F16: com a chave certa o topo de cada pino de chave fica na linha de corte; sem chave o pino superior atravessa a linha); duração igual à da voz; chave parada de S07 a S09; rotor
travado ao fim da S09 e livre ao fim da S11; a chave só avança; pinos nunca passam do teto da câmara; todos os valores entre 0 e 1 em cada um dos 2167 frames.

## Desvios do `plano-animacao.md` (decididos por mim; o dono pode trocar)
1. **S04 e S05:** o plano pedia a montagem na S04 e uma vista "vazia" de novo na S05. Montei tudo na S04 (colunas da esquerda para a direita) e, da S05 em diante, uso **foco e rótulo**
   (grupos esmaecem e voltam na cena em que são explicados), sem remontar.
2. **S07:** o plano pedia linhas finas ligando o fundo de cada corte da chave ao pino da mesma coluna ("corresponde"). Neste enquadramento a chave (690 px) não cabe ao lado do rotor com os
   cortes sob as colunas, então a S07 só destaca os pinos de chave, um a um, com o rótulo. As linhas ficam para uma segunda versão (chave acima ou abaixo da vista, ou vista maior).
3. **S06:** a chave entra pela esquerda e para no canal; os cinco furos pulsam. O `number` "5 ou 6" é outro plano (template), não está neste clipe.
4. **S09:** a seta curva do rotor aparece com um "X" (rotor não gira). A caixa-preta "Mecanismo da trava" e o came **não** estão neste clipe (entram na S14).
5. **Tempos dentro de cada cena** são frações da duração da cena (estimativa pela posição das palavras). O tempo exato por palavra só sai do `vp render`, com as âncoras de `scenes.json`.
6. **Fora deste clipe:** S12 e S13 (vista de frente e giro do rotor), S14 em diante, o cadeado, a tranca egípcia e as cenas S17–S23.

## Para reproduzir um quadro
`cd video && TMPDIR=<pasta em data/cache/remotion-tmp> npx remotion still src/previews/mec-fechadura-pt/index.tsx FechaduraClipe ../renders/mec-fechadura-pt/clipe/q-NNNN.png --frame=NNNN`
(pastas temporárias de teste: `data/cache/remotion-tmp/piloto-fechadura` e `piloto-fechadura-2`, a apagar quando quiser).
