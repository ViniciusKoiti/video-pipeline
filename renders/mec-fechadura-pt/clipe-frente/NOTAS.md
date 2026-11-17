# Vista de frente (S12 e S13), traço limpo — notas de 2026-11-09

Código: `video/src/previews/mec-fechadura-pt/` (`vistaFrente.ts` geometria, `linhaDoTempoFrente.ts` linha do tempo, `frente.tsx` desenho, `tempos-frente.json`, `check-frente.mjs`; a composição
`FechaduraClipeFrente` está em `index.tsx`). 1280×720 a 30 fps, 481 frames (16,03 s) = S12 (9,00 s) + S13 (7,04 s) da voz (`voice/leveled/*.wav`). Sem commit. **Só quadros; nenhum vídeo.**
`paleta.ts` saiu do `index.tsx` para as duas vistas compartilharem as cores (o clipe S04–S11 não mudou; `check.mjs` continua passando).

Quadros: `q-0020` (brilho na linha livre, vista lateral), `q-0060` (meio do giro de câmera), `q-0100` e `q-0150` (vista de frente com rótulos), `q-0215` (rotor girando),
`q-0269` (fim da S12, rotor girado), `q-0300`, `q-0335`, `q-0400`, `q-0440` (S13, câmera no pino de chave e depois na pilha), `q-0450`, `q-0480` (fim, tudo rotulado).

## O que o `check-frente.mjs` confere
Geometria (a linha de corte é a borda do rotor; topo do pino de chave e fundo do pino superior ficam nela, F16; mola com comprimento; o pino de chave vai às 3 h com 90°); tempos iguais aos da voz;
todos os valores entre 0 e 1 nos 481 frames; o rotor só gira depois de a vista de frente abrir; a câmera só se move na S13; os rótulos da S13 entram na ordem da fala (pino de chave, pino superior, mola).

## Desvios do `plano-animacao.md` (decididos por mim; o dono pode trocar)
1. **Giro de câmera de 90°** é simulado: a vista lateral fecha em `scaleX` enquanto a de frente abre. Não é perspectiva 3D de verdade (a pergunta do 3D é a outra frente).
2. **S12:** o brilho na linha livre (S11) vem antes do giro; "Chave" aparece na vista de frente só como seção da lâmina e some quando o rotor começa a girar. A seta curva é externa ao rotor.
3. **S13:** o desenho só mostra o estado depois do giro (F25), sem movimento; a câmera vai do pino de chave à pilha das 12 horas e recua no fim. Os rótulos laterais (Carcaça, Rotor, Linha de corte,
   Pino de chave) saem durante o zoom, para não serem cortados, e Carcaça, Rotor e Pino de chave voltam no recuo.
4. **O pino superior assenta na superfície do rotor** (que é sólida às 12 h depois do giro). Não aparece o furo vazio do rotor nesse lugar, porque ele foi com o rotor.
5. **Tempos dentro de cada cena** são frações da duração (estimativa pela posição das palavras); o tempo exato só sai do `vp render`.
6. **Fora deste clipe:** S14 (came e "Mecanismo da trava"), o cadeado, a tranca egípcia e S17–S23. O `keyword` da S12 e da S13 e o rodapé de fonte são planos do template, não estão aqui.

## Para reproduzir um quadro
`cd video && TMPDIR=<pasta em data/cache/remotion-tmp> npx remotion still src/previews/mec-fechadura-pt/index.tsx FechaduraClipeFrente ../renders/mec-fechadura-pt/clipe-frente/q-NNNN.png --frame=NNNN`
(pasta temporária de teste: `data/cache/remotion-tmp/piloto-fechadura-3`, a apagar quando quiser).
