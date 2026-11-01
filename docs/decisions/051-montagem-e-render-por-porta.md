# ADR 051 — Montagem e render por porta, com as pré-condições na operação

Data: 2026-11-01. Status: aceita. Fatia 4 do RF6 do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md). Concretiza o que o ADR 042 deixou como proposta
para o `render`.

## Contexto

O fim do `main` do `montar_episodio.py` instanciava `RemotionEngine()` direto, escolhia `preview.mp4` ou
`final.mp4` por uma bandeira, gravava o `episode.json` com `write_text` e mandava renderizar. Nada conferia o
gate 4: renderizar de novo por cima de uma prévia ou de um final aprovados, ou regravar o `episode.json` e o
`captions.srt` que o gate carimba, tirava a aprovação sem aviso. O render final não exigia os ativos aprovados.

## Decisão

- **`EpisodeRenderer`** (`app/pipeline/assembly.py`) recebe a porta de render por formato (`Context.renderer`,
  da composição) e faz `assemble` (confere e grava o `episode.json`) e `render`. O motor é o que o
  `providers.toml` liga ao formato do episódio; trocá-lo é uma linha de configuração, e os testes o trocam por um
  renderer falso. Formato sem motor é `ConfigurationError`, antes de qualquer escrita. Hoje o `RemotionEngine` da
  composição e o do script têm os mesmos parâmetros (`crf`, `fade`, presets), então a saída não muda.
- **Pré-condições da operação**, sob o lock do episódio e antes de escrever: toda cena tem o WAV íntegro; todo
  ativo usado (planos, inclusive a forma v1 de uma cena, e a trilha) tem o arquivo de mídia. O **render final**
  exige ainda todos esses ativos aprovados (`review_status`, gate 3); a **prévia** é rascunho e não exige (as
  condições propostas no ADR 042, mantidas). Falta é `AssemblyError`, listando tudo o que falta; o motor não é
  chamado e nem o `episode.json` é gravado.
- **Prévia e final são arquivos diferentes** (`renders/preview.mp4`, `renders/final.mp4`), cada um com o seu
  carimbo no gate 4 (#120): o `WriteGuard` (ADR 039) é consultado para o MP4 de saída antes do motor, e o gate 4
  aprovado para aquele arquivo recusa o render por cima (reabrir libera); renderizar o outro é permitido, e a
  aprovação passa a pedir nova decisão. O `episode.json` igual ao que está lá não é regravado (e não pede o guard); o
  novo passa pelo guard e vai inteiro (`write_atomic`): falha mantém o antigo e não chega ao motor.
- **`captions.srt`:** `sync_captions` ganhou `before_change`, chamado com o texto novo antes de qualquer escrita ou
  renomeação para `captions.old.srt`; o `montar_episodio.py` o liga ao guard, então o gate 4 aprovado recusa a troca
  da legenda sem tocar no arquivo (a legenda mantida não passa pelo gancho).
- `montar_episodio.py` usa `EpisodeRenderer` e `context.renderer`; `--no-render` chama só `assemble`.

## Fora do escopo

`subs` e `voice` como operações separadas e o `Production` (o `main` do script segue sequencial); a escrita do
`captions.words.json` (não é carimbado pelo gate 4); o `description.txt` e o `credits.txt` do `vp export`; teste
visual real, que segue o vídeo-régua e as autorizações atuais.
