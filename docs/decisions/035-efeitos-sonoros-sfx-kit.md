# 035 — Efeitos sonoros nos Shorts: o SFX Kit (CC0) como catálogo e um `sfx.json` por vídeo

- **Status:** proposta; o `sfx.json`, a conferência e a mistura no `juntar` estão implementados e testados; o
  primeiro vídeo com efeitos espera a escuta do dono.
- **Data:** 2026-10-31
- **Relaciona-se com:** ADR 007 (licenças; CC0 na lista fechada), ADR 008 (planos ancorados na narração),
  ADR 009 (quem escreve dados não aprova; o código valida), ADR 030 (trilha: o mesmo desenho, para música), a
  skill `shorts-tec`.

## Contexto

Os Shorts técnicos saem só com a voz clonada sobre o render silencioso. Um Reel de referência analisado em
2026-10-31 (forma, não conteúdo) mostrou o padrão do nicho: um som na entrada de cada cartão, um tique no número
que sobe, um sinal no check verde, e a voz sempre clara por cima. O fluxo de 8 passos que o dono trouxe pede o
mesmo (passo 7, "sound design"). O pipeline cobre roteiro, planos, animação e trilha; efeitos sonoros não
existiam em lugar nenhum.

Três ferramentas foram conferidas na fonte (não só na descrição do vidIQ):

- **SFX Kit** (Wyzowl): 320 efeitos sintetizados em código, WAV 48 kHz, **CC0 1.0**, com dados para colocar
  cada som (`sync.at`, `timing`, `under_voiceover_db`, `use_for`, `avoid_for`, `fits_seconds`, `sha256`).
- **earshot** (MIT; modelos Apache-2.0 e BSD-3): CPU, offline depois de baixar ~1,1 GB de modelos; descreve
  e julga áudio, mede batidas e sincronia com os cortes, gera 252 efeitos em código.
- **Openverse** (API aberta, 20/min e 200/dia sem chave): busca em acervos; devolve licença e atribuição por
  item, mas o arquivo é o preview MP3 do Freesound (o original pede chave de outro provedor).

## Decisão

1. **O SFX Kit é o catálogo**, clonado pelo dono em `data/sfx/kit/` (fora do Git, como `data/music/`). O
   `sounds.json` dele é lido direto: não se duplica o catálogo. A licença é CC0, da lista fechada da ADR 007, e
   o `sha256` de cada WAV é conferido antes do uso (regra 3). Som sintetizado em código: sem pessoa, marca nem
   gravação de terceiro para conferir.
2. **Um `sfx.json` por vídeo**, no mesmo desenho do `music.json` (ADR 030): cada efeito (cue) é um som do kit num
   momento de uma cena; o momento é o começo da cena, mais a posição de um trecho da narração na fala real
   (como a âncora de um plano), mais um deslocamento em segundos. O som começa no momento menos o `sync.at` do
   kit e desce o `under_voiceover_db` onde o corpo dele cai sobre a fala. Os efeitos sobem ou descem juntos pela
   diferença entre a voz medida e a referência do kit (−16 LUFS), para a relação voz/efeito ser a que o kit
   mediu.
3. **O código confere o que não depende de ouvir** (`app/pipeline/sfx.py`): som no kit e com o hash certo, cena
   e âncora existentes, momento dentro da cena, aviso quando um som que o kit marca como "cobre a voz" cai sobre
   a fala e quando passam de 8 efeitos em 10 s. Quem ouve é o dono, na prévia (gate 4).
4. **A mistura é na junção** (`shorts_tec.py juntar --sfx=<sfx.json>`), no mesmo grafo do ffmpeg das falas:
   cada efeito é uma entrada a mais com corte, ganho e atraso; o loudnorm final continua valendo para o
   conjunto. Trocar um efeito refaz só a junção, nunca o render.
5. **earshot entra depois, como conferência**, não como decisor: o `timeline` sobre o MP4 final diz se cada
   efeito caiu no corte, e o `match` deixa o agente ouvir a trilha antes do dono (limite declarado da ADR 030).
   Só com pedido do dono, pela sonda de CPU, e com os modelos em cache. **Openverse** só para um som que o kit não
   tem, como adapter de busca (`search_assets()`), com os termos registrados antes (§7); não está no plano.

## Trade-offs

- **Os momentos são da cena e da fala, não da animação.** O `motion-video` não exporta quando cada cartão entra
  dentro da cena; o plano aponta o corte (começo da cena) e as palavras ditas, mais um deslocamento a olho. Um
  som num cartão que entra no meio da cena pede o deslocamento certo, que hoje é chute do montador. Se o kit
  passar a exportar os eventos da cena, eles viram a terceira âncora.
- **Sem mudança de velocidade.** O kit permite `adapt.rate`; a v1 não usa (um whoosh fica no tamanho que é).
- **O agente não ouve.** Como na trilha; o earshot pode mudar isso, mas é outra decisão.
- **Shorts por JSON só.** O `explainer` (Remotion, `episode.json`) não mistura efeitos; mudar o `episode.json`
  pede ADR própria.

## Consequências

- Implementado: `app/pipeline/sfx.py` (modelos, leitura do kit, conferência e colocação), `juntar --sfx` e o
  verbo `sfx` do `shorts_tec.py`, `tests/test_sfx.py`. `.gitignore` ignora `data/sfx/*`.
- Piloto: `renders/short-lista-ligada/sfx.pt.json`, 13 efeitos em 38 s, misturado numa saída nova
  (`renders/final-sfx.mp4` do episódio `-pt`), sem tocar no `final.mp4` carimbado pelo gate 4 nem no vídeo
  publicado. A escuta do dono decide se o próximo Short sai com efeitos.
- **Emenda de 2026-10-31 (earshot no pipeline, decisão do dono "para vídeos maiores"):** instalado em ambiente
  próprio (`EARSHOT_PYTHON`; termos e primeira medida em `data/benchmarks/termos-earshot.md`) e registrado como
  servidor MCP do usuário. Entra como **conferência depois da junção**, nunca como decisor:
  `scripts/provisorio/conferir_audio.py <mp4> --episodio=<id>` (longo, cortes do `episode.json`) ou
  `--content=<content.voz.json> [--sfx=<sfx.json>]` (Short), via `app/media/earshot.py`. Devolve a loudness como o
  YouTube mede, o pico real, a batida da trilha e a sincronia dos cortes; problema = loudness fora do alvo, pico
  acima de −1 dBTP ou corte com efeito planejado sem ataque a 40 ms. A primeira medida mostrou que o Short mono
  está a −12 LUFS efetivos enquanto o `ebur128` diz −15; o que fazer com o `juntar` (estéreo ou alvo −3 dB no mono)
  é decisão pendente do dono.
- Pendente: o mesmo plano no `-en` (as âncoras de texto mudam de idioma; o gate de tradução da ADR 034 não
  cobre o `sfx.json`), a nota na skill `shorts-tec`, o earshot como check, e a hipótese de retenção com e sem
  efeitos, medida aos 7 e 28 dias.
