# 059 — Plano `cast`: personagem do motion-kit sobre fundo ilustrado, no formato explainer

- **Status:** proposta (2026-11-13). Nada implementado. O piloto `academia-dinheiro-pt` segue pelo caminho
  provisório (clipe por cena registrado como ativo); esta ADR decide o caminho definitivo, se o formato pegar.
- **Data:** 2026-11-13
- **Pedido do dono:** "a e b" (2026-11-13): clipe por cena agora (a) e plano próprio no template (b).
- **Relaciona-se com:** ADR 001 (um motor por formato), ADR 007 (licenças: `Generated` e `Original`), ADR 008
  (cena e planos, âncoras na narração), ADR 013 e 029 (apresentador e pele em camadas), ADR 027 (tarball do kit em
  `video/vendor/`), ADR 031 (B-roll como textura), emenda de 2026-11-09 da ADR 007 (clipe animado do projeto).

## Contexto

O formato "mascote em cenário ilustrado" (referência: Lucro Disfarçado) põe o mesmo personagem em quase todos os
planos, sobre um fundo desenhado. No piloto, o personagem é a capivara economista, desenhada em código no motion-kit
(`createCapivaraSkin`, subcaminho `@viniciuskoitin/motion-kit/host/figure`, versão 0.12.0, licença MIT/`Original`),
e os fundos são imagens geradas sem personagem (`Generated`), reaproveitadas com outro enquadramento por cena.

O `scenes.json` e o `episode.json` (v2) não têm plano para "personagem agindo sobre um fundo". Hoje há duas saídas:

- **(a) Clipe por cena:** uma composição TSX monta fundo e personagem com o `<CastScene>` do kit, renderiza um MP4 por
  cena ou por plano, e o MP4 entra como ativo `Original` num plano de vídeo (`broll`). O contrato do render não muda.
- **(b) Plano `cast`:** o template do explainer desenha o personagem sobre o fundo no próprio render, a partir de
  dados do plano. O contrato muda.

## Decisão proposta

Adotar (b) se o piloto for aprovado no gate 4 e o formato continuar. Até lá, (a).

Plano novo `cast` no `scenes.json` e no `episode.json` (versão nova do contrato, por isso esta ADR):

| Campo | Conteúdo |
|---|---|
| `background` | `asset_id` de um fundo aprovado no gate 3 (`Generated`), mais `blur` e `zoom` opcionais |
| `actor` | pele por nome (`capivara`, ou `capivara-costas`), `x`, `z`, `size`, `facing` |
| `actions` | lista de `walkTo`, `turn` e `gesture`, cada uma com âncora na narração (como os planos, ADR 008) |
| `expressions` | lista de expressões com âncora |
| `camera` | `follow` ou avanço (`push`), e quadro (`full`, `bust`, `face`) |
| `floor` | `floorY` e `wallY` do fundo (medidos uma vez por fundo e guardados no ativo) |

- O tempo de cada ação sai da posição da âncora sobre a duração real do WAV, como nos outros planos.
- O `vp check` valida: o fundo é ativo aprovado, as âncoras existem na narração, a pose e o gesto existem na pele, e
  a ação cabe no plano.
- Os direitos ficam separados: o fundo responde como `Generated` (divulgação de conteúdo sintético) e o personagem
  como `Original`. Um clipe de (a) mistura os dois num arquivo só, e é por isso que (a) é provisório.
- O template passa a depender do kit 0.12.0 ou maior; trocar o kit no template pede versão nova da vídeo-régua.

## Consequências

- **(b) a favor:** o ajuste de uma pose ou de uma âncora refaz só aquela cena no render (cache por cena), sem
  renderizar clipe à parte nem registrar ativo novo; os direitos de fundo e personagem ficam rastreáveis em separado;
  o roteirista e o `vp check` passam a enxergar a encenação.
- **(b) contra:** mexe no contrato do render, no template e nos schemas; exige testes de template; prende o template
  a uma API do kit que ainda está mudando (pose sentada, transições de gesto).
- **(a) no piloto:** mais rápido de começar e não mexe no contrato, mas cada mudança pede novo render de clipe e novo
  registro de ativo, e o ativo mistura duas licenças.

## Pendências

- Kit: pose sentada (6 cenas do piloto) e movimento (repouso e transição de gesto), pedidos pelo dono depois do
  feedback de 2026-11-13. Fixar a versão do kit no template uma vez só, já com isso.
- Dono: aprovar ou recusar esta ADR depois do gate 4 do piloto.
