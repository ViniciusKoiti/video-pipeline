# 014 — Perfil vertical (9:16) do formato explicativo

- **Status:** aceito (2026-10-05; o dono respondeu as duas perguntas e aceitou)
- **Data:** 2026-10-05
- **Etapa do roadmap:** frente do apresentador, B2 (o B1 é a ADR 013)
- **Relaciona-se com:** ADR 001 (motor por formato), ADR 007 (contratos), ADR 008 (planos), ADR 011 (planos
  editoriais), ADR 013 (apresentador em janela)

## Contexto

Os vídeos curtos (Reels, Shorts, TikTok) são 9:16. Hoje o contrato recusa qualquer quadro que não seja 16:9
(`VideoSpec`), a prévia vale `720 × 16 / 9` (`app/render/base.py`) e o template inteiro foi desenhado em paisagem:
`video/src/Editorial.tsx` e `ShotView.tsx` medem tudo por `u(height, px)` (px × altura ÷ 1080), com gráficos de
1600 px, canvas de rede de 1280×720, invólucro de 1920×1080 e margens laterais de 160 px. Num quadro 1080×1920 essa
escala pela altura quase dobra tudo e as margens passam de um quarto da largura. O `<FloatingWindow>` e o `<Host>`
do motion-kit já têm área segura (`safeArea`) para vertical.

## Opções consideradas

1. **Todos os planos em retrato.** Cobre rede, mapa, linha do tempo e árvore, que dependem de canvas largo: várias
   etapas de redesenho, sem caso de uso imediato nos vídeos curtos.
2. **Faixa 16:9 no meio do 9:16.** Pouco código, mas o texto fica ~56% menor e ilegível no celular.
3. **Só os planos que cabem em retrato** (escolhida). O perfil vertical aceita `photo`, `broll`, `number`, `keyword`,
   `stamp`, `lower_third`, `compare` e `chart`; recusa os outros no contrato.

## Decisão

- **Contrato.** `scenes.json` ganha `orientation` (`landscape` padrão ou `portrait`). `VideoSpec` aceita 16:9 ou
  9:16 (1920×1080 e 1080×1920 como padrões) e `EpisodeManifest` o deriva de `video`. O vertical só existe no
  formato `explainer` (o motor ffmpeg do documentário continua 16:9). No vertical, qualquer plano fora de
  `PORTRAIT_SHOT_KINDS` é erro de validação em `scenes.json` e em `episode.json`, e o `vp check` o aponta com o
  nome do plano.
- **Unidade.** O template mede por `u = px × lado curto ÷ 1080`: o mesmo valor em px de projeto vale nos dois
  perfis (em paisagem, lado curto = altura, nada muda). Um gancho do template substitui `u(height, …)`.
- **Prévia.** 720 × 1280 no vertical (lado curto 720, como hoje).
- **Layout em retrato.** Cada plano do subconjunto ganha o seu arranjo: o número e o carimbo caem de tamanho até
  caber na largura, a comparação empilha (`layout="vertical"` do kit), o gráfico usa a tela de projeto 1080×1920
  com 940 px de largura, a frase quebra na largura do quadro, e a foto e o B-roll preenchem o quadro. As peças do
  kit medem pela altura (`useUnit`); o template as alimenta com props em px finais (`kit()` em `theme.ts`). A fonte
  do plano vai sempre para o topo da área segura: o painel do número e a tarja ocupam a largura embaixo.
- **Área segura.** Legenda, fonte, tarja, carimbo e janela do apresentador ficam dentro da área segura `vertical`
  do kit (1080×1920: topo 288, base 500, direita 140, esquerda 60 px). Número, comparação e gráfico usam o quadro
  todo, centralizados, e podem passar um pouco para os lados (escolha do dono, 2026-10-05).
- **Apresentador.** A janela usa a área segura automática do kit e fica logo abaixo da fonte do plano.
  `HostSpec.width` passa a ser opcional, com padrão 0,16 em paisagem e 0,28 em retrato (a largura é fração do
  quadro, e o quadro é mais estreito; 0,32 invadia o conteúdo centralizado). Em retrato só os dois cantos de cima
  são livres: a base segura (500 px) coloca os de baixo no meio do quadro, onde fica o conteúdo. A regra de cantos
  (`app/media/host.py`) bloqueia os de baixo sempre, o de cima à esquerda no selo de canto, o de cima à direita na
  comparação empilhada (que começa alto) e os dois de cima no gráfico; sem canto livre, a janela fica onde estava.
- **Legendas.** No vertical, o final sai com a legenda queimada na imagem (padrão dos vídeos curtos, escolha do
  dono em 2026-10-05) e o SRT continua sendo gerado e editável. No paisagem nada muda: o final sem legenda
  queimada e a prévia com. A legenda queimada fica acima da base segura.
- **Fora desta ADR:** rede, mapa, linha do tempo, árvore e cartão de documento em retrato; música; export para
  plataforma; título e capa.

## Consequências

- `app/pipeline/schemas.py` (`orientation`, `VideoSpec`, `PORTRAIT_SHOT_KINDS`, validação), `app/render/base.py`
  (prévia), `app/render/remotion.py` (largura e altura nas props), `app/media/host.py` (tabela do retrato),
  `app/pipeline/check.py` (erro por plano), `video/src/*.tsx` (unidade e layouts), `scripts/provisorio/
  montar_episodio.py`, `CLAUDE.md` (§6 e §9) e testes.
- A troca de `u(height, …)` toca quase todo `Editorial.tsx` e `ShotView.tsx`: o `template_hash` muda e o primeiro
  render depois do merge refaz as cenas. Em paisagem o resultado visual não pode mudar: a folha de quadros da
  régua (`evolucao.py comparar`) tem de mostrar zero planos mudados.
- Teste visual: S01–S05 da régua em 9:16 na cópia local `votorantim-apresentador`, que só usa planos do subconjunto.
