# 057 — Grade de cor (preto e branco) por ativo de B-roll

- **Status:** proposta (2026-11-10). Implementada no código e usada em `nietzsche-solo-leveling-sistema`; a confirmar
  pelo dono.
- **Data:** 2026-11-10
- **Relaciona-se com:** ADR 007 (emenda de 2026-11-03, item 3: grade de cor, inclusive preto e branco, vale como
  escolha de estilo do canal), ADR 031 (B-roll como textura), ADR 038 e 045 (constantes e erros)

## Contexto

Pedido do dono (2026-11-10): os dois clipes do trailer de *Solo Leveling* saem em preto e branco, e só eles. O
preto e branco é **estilo do canal** (ADR 007). Não é proteção de direitos: a emenda da ADR 007 proíbe espelhar a
imagem e mudar a velocidade ou a altura do áudio para escapar da detecção, e a reivindicação continua esperada
(item 7). O que sustenta o clipe é a citação: sem o áudio da obra e só enquanto a narração o comenta.

`scenes.json` e `assets/*.json` são carimbados pelos gates 2 e 3; um campo de cor neles derrubaria as duas decisões.

## Decisão

- `tratamento.json` na pasta do episódio, fora de qualquer carimbo: `{"mono": ["id-do-ativo", ...]}`.
  Sem o arquivo, nada muda. Formato inválido é erro (`GradeInvalid`).
- O motor do Remotion acrescenta `grade: "mono"` ao plano `broll` cujo `asset_id` está na lista, e só a ele; as
  props (e o cache) dos outros planos ficam como estavam.
- O template aplica `filter: grayscale(1)` só ao vídeo do `broll`. Texto, legenda, tarja, apresentador e fotos não
  mudam. O `episode.json` não muda.

## Consequências

- Mudar `video/src/*.tsx` muda o `template_hash`: o primeiro render depois refaz todas as cenas.
- A lista vale por ativo, em todos os usos dele no episódio. Não há grade por plano nem outras cores.
- O `vp check` ainda não confere se os ids da lista existem; o render só aplica aos que aparecem.
