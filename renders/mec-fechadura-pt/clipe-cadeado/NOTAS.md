# Came e bloco da trava (S14) e cadeado em corte (S15 e S16), traço limpo — notas de 2026-11-09

Código: `video/src/previews/mec-fechadura-pt/`. Geometria e cinemática em `cadeado.ts`; desenho em `cadeadoVista.tsx` (S15–S16) e `came.tsx` (S14); linhas do tempo em `linhaDoTempoCadeado.ts`;
`tempos-cadeado.json`; conferência em `check-cadeado.mjs`; composições `FechaduraClipeCame` (S14, 222 frames, 7,40 s) e `FechaduraClipeCadeado` (S15 + S16, 629 frames, 20,96 s) em `index.tsx`.
1280×720 a 30 fps, durações = voz (`voice/leveled/*.wav`). Sem commit. **Só quadros; nenhum vídeo.**

Quadros: `../clipe-came/q-0000, 0014, 0045, 0080, 0120, 0150, 0221` (S14: vista de frente fecha, a lateral abre, came e bloco entram, a alavanca gira com a chave e toca o bloco);
`q-0020, 0060, 0140, 0200, 0260, 0321` (S15: a vista da fechadura encolhe para o canto, o cadeado entra e os rótulos vêm na ordem da fala) e
`q-0400, 0450, 0490, 0540, 0628` (S16: o came gira, os trincos recuam contra a mola, a haste fica solta e a mola a empurra para fora).

## O que o `check-cadeado.mjs` confere
- **Cinemática:** com o came girado de 0° a 90° o recuo dos trincos vai de 0 a ~50 px; o braço (cunha) fica sempre encostado no came e nunca dentro dele (amostragem de 0,4 px no contorno);
  a mola do trinco nunca zera; a ponta do trinco encaixa no fundo do entalhe em repouso e sai dele no fim; o trinco de baixo é o de cima espelhado pelo eixo do came.
- **Ordem física:** a haste só sobe depois que os trincos saíram dos entalhes e depois de o came terminar o giro; a S15 não mexe em nada no cadeado.
- **Tempos e rótulos:** durações iguais às da voz; todos os valores entre 0 e 1 em cada frame; rótulos da S15 na ordem da fala (No cadeado, Came, Trincos, Mola, Entalhes, Haste); na S14 o bloco só acende quando a
  alavanca o toca (a ponta dela a 90° fica exatamente na face do bloco).

## Escolhas minhas que o dono ou o verificador devem olhar (a fonte não as dá)
1. **Forma do braço do trinco:** `source-03#E54` diz que o braço "repousa na borda reta do came, um por cima e outro por baixo, e que o giro do came puxa os braços para dentro, contra a mola". Não descreve o
   formato. Desenhei o braço como uma **cunha de 45°** que sobe pelo came para o recuo horizontal do trinco ficar contínuo. É esquema didático; nenhuma ficha diz "cunha".
2. **Folga do came:** nos primeiros ~35° do giro os trincos quase não se mexem (o came ainda está em repouso sob a cunha) e só então recuam. Isso vem da forma que escolhi, não da fonte.
3. **Came como "palito" arredondado e rotor de frente:** o cadeado é visto como em corte transversal ao eixo (o rotor é o círculo azul com a fenda da chave); o came é desenhado por cima dele.
4. **S14 em vista lateral, como no plano:** a alavanca é um esquema (barra que gira para tocar o bloco); a vista de frente da S13 gira de volta para a lateral no começo da S14 (mesmo truque de `scaleX` da S12).
5. **Trinco "de cima" à esquerda e "de baixo" à direita:** o giro horário do came os puxa para dentro. A fonte não diz qual lado; o desenho é simétrico por escolha.
6. **Tempos dentro de cada cena** são frações da duração (estimativa pela posição das palavras); o tempo exato só sai do `vp render`.
7. **Fora deste clipe:** o `number` "2" da S15, o `keyword` da S14 e o rodapé de fonte (planos do template); a tranca egípcia e as cenas S17–S23.

## Para reproduzir um quadro
`cd video && TMPDIR=<pasta em data/cache/remotion-tmp> npx remotion still src/previews/mec-fechadura-pt/index.tsx FechaduraClipeCame|FechaduraClipeCadeado <saida.png> --frame=N`
(pasta temporária de teste: `data/cache/remotion-tmp/piloto-fechadura-3`, a apagar quando quiser).
