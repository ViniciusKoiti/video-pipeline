# Scripts provisórios: onde entram no fluxo hoje e como entrariam no `app/` (mapa de 2026-10-31)

Mapa, não implementação: nada foi movido. Conferido na árvore local (branch `serie-conceitos-short-1`,
2026-10-31) lendo os 18 scripts de `scripts/provisorio/` (2.745 linhas), o `app/cli.py`, o `app/bootstrap.py`,
as skills e agentes que os chamam, os testes que os carregam e as issues #188–#193 (gaps G1–G6 de 2026-10-23).
Complementa `docs/diagramas/mermaid/pipeline-hoje.mermaid` (onde cada script aparece) e `docs/analise-gaps-tecnicos.md` (removido em 2026-11-01; no histórico do Git; G4 é o
`montar_episodio.py` fora das proteções do núcleo). O §5 traz o desenho em objetos: o que vira classe, o que
vira valor e o que fica função, no estilo que o `app/` já usa.

**Execução a partir de 2026-11-01:** seguir o
[fluxo com gates RF0–RF7](fluxo-refatoracao-solid-2026-11-01.md), que incorpora os gaps de SOLID e ajusta a
ordem do §6: proteção e retomada precedem a migração da produção; a porta TTS precede a extração do narrador.

## 1. Onde cada script está no fluxo hoje

| Faixa (`pipeline-hoje.mermaid`) | Script | Quem chama | Momento |
|---|---|---|---|
| Prova, longo e Reel | `radar_resumo.py` | skill `pauta` (ADR 018) | antes da pauta do Reel |
| | `formato_resumo.py` | skill `analise-de-formato` e `brief.py` dela (ADR 031 B) | antes do roteiro do longo |
| | `baixar_fonte.py` | dono ou agente, com pedido do dono na sessão | antes do pesquisador |
| | `fonte_declarada.py` | dono (receita, nota) | antes do pesquisador |
| | `checagem_local.py` | dono, medição do #27 | fora da cadeia; benchmark |
| Produção, longo | `buscar_candidatos.py` | skill `plano-de-imagens` | entre o gate 2 e o gate 3 |
| | `baixar_escolhidos.py` | skill `plano-de-imagens`, depois da validação do dono | antes do gate 3 |
| | `catalogo_musica.py` | agente `diretor-musical`, skills `trilha` e `vp-trilha` | depois do gate 2 (ADR 030) |
| | `montar_episodio.py` | dono; `evolucao.py` por subprocesso; `shorts_tec.py` importa dele | voz, legenda, `episode.json`, render |
| | `evolucao.py` | dono, vídeo-régua (CLAUDE.md §1) | ao fim de cada PR de visual |
| | `livros_afiliado.py` | dono (CLAUDE.md §4, `config/canal.toml`) | descrição, antes do gate 4 |
| Produção, Short | `shorts_tec.py` | skills `shorts-tec` e `short-diario` (ADR 033, 035, 036) | voz, tempos, sfx, junção, boca, pasta de gate |
| | `conferir_audio.py` | skill `short-diario`, dono (ADR 035) | depois da junção |
| Saída | `shorts_tec.py gate` | skill `short-diario` | antes do gate 4 |
| | `metricas.py` | dono (§12) | 7 e 28 dias depois de publicar |
| Fora do fluxo | `clipe_reconhecer.py`, `clipe_tempos.py` | clipe de letra (composição `Clipe`, Nabote) | uma vez |
| | `sprites_apresentador.py` | pele do dono (ADR 017, 029); dado pessoal | uma vez por pele |
| | `teste_voz_gemini.py` | escuta cega de 2026-09-30; superado pelo adapter Gemini e pela voz clonada | histórico |

Como são chamados: `uv run --no-sync python scripts/provisorio/<nome>.py ...` ou `.venv/bin/python ...`. Cada um
faz `sys.path.insert(0, ROOT)` e monta o próprio contexto (`load_settings(ROOT)` ou `build_context(ROOT)`),
fora do `Context` que o `vp` monta uma vez só.

## 2. Inventário: o que cada script carrega de lógica própria

"Lógica própria" é o que não existe em `app/` e teria de ser movido; "já em `app/`" é o que o script só costura.

| Script | Linhas | Lógica própria | Já em `app/` | Testes que carregam o script |
|---|---|---|---|---|
| `montar_episodio.py` | 325 | `voice_fingerprint` (lê `settings` por provedor e importa `reference_hash` do adapter Chatterbox), `long_speech_tag` (importa `MAX_PART_CHARS` do adapter), chave do WAV (pausa, entrega, glossário), `batches` e `generate` (lotes do Gemini, cena a cena no erro), `media_path`, `music()` (faixa do episódio), costura de `captions()` e `word_captions()`, montagem do `EpisodeManifest` v2, `RemotionEngine()` direto, loudness ao fim | `captions`, `word_captions`, `narration`, `pauses`, `probe`, `pronunciation`, `shots`, `music`, `loudness`, `RemotionEngine` | `test_chatterbox_tts.py` (`voice_fingerprint`, `long_speech_tag`), `test_narration.py` (`batches`) |
| `shorts_tec.py` | 553 | `Line`/`load_lines`, `wav_name`, `bounds_from_log`/`speech_bounds` (silêncios das pontas pelo `silencedetect`), `fit_durations`, `scene_starts`, `mix_filter` (filtro do ffmpeg: fala, áudio do render, efeitos, estéreo, loudnorm), `cmd_voz`, `cmd_tempos`, `sfx_placed`/`cmd_sfx`, `cmd_juntar`, `cmd_boca`, `cmd_gate` | `loudness`, `probe`, `pronunciation`, `envelope`, `pipeline/sfx.py` | `test_shorts_tec.py` (6 funções), `test_sfx.py` (`mix_filter`) |
| `buscar_candidatos.py` | 127 | `available_archives` (lê `DEFAULT_REGISTRY` direto para pular banco sem adapter ou sem chave), orientação pelo `scenes.json`, laço consulta × mídia × banco, registro de candidatos e falhas em `candidatos/<pedido>.json` | adapters Pexels, Pixabay, Unsplash; `AssetQuery`, `AssetCandidate` | nenhum |
| `baixar_escolhidos.py` | 57 | leitura dos candidatos, sufixo do arquivo, `download_asset`, `sha256`, `assets/<id>.json` em `needs_review` | adapters, `sha256_file`, `Asset` | nenhum |
| `baixar_fonte.py` | 92 | próximo `source-NN`, download ou `--file`, detecção de PDF, `pdftotext`, gravação de raw, txt, trechos e `sources.json` | `extract.py`, `excerpts.py`, `http.download`, `JsonFileStore` | nenhum |
| `fonte_declarada.py` | 83 | `line_paragraphs`; o mesmo registro do `baixar_fonte.py`, duplicado | idem | nenhum |
| `catalogo_musica.py` | 164 | `slug`, `add` (ativo + faixa + linha do catálogo), `use` (copia para `assets/`), `listar` | `music.py` (`load_music_catalog`, `resolve_music`), `loudness.intensity`, schemas `MusicTrack`, `MusicCatalog` | nenhum |
| `evolucao.py` | 136 | `template_info` (git, `git archive` de um commit), `save`; `gerar` chama o `montar_episodio.py` por subprocesso com `--preview --voz=gemini` | `media/evolution.py` (tudo o mais), `remotion.template_hash`, `bench.cpu_probe` | nenhum |
| `conferir_audio.py` | 124 | `cuts_from_episode`, `cuts_from_content` (importa `scene_starts` do `shorts_tec.py`), `expected_from_sfx`, sonda de CPU, impressão | `media/earshot.py`, `pipeline/sfx.py` | nenhum |
| `metricas.py` | 196 | só argparse e os parsers `_origem` e `_pedido` | `pipeline/metrics.py` (tudo) | `test_metrics.py` |
| `radar_resumo.py` | 78 | `RADAR_DIR`, cópia datada com `--atualizar` | `pipeline/radar.py` | nenhum |
| `formato_resumo.py` | 56 | a mesma cópia datada, duplicada | `numbers.py` (`FormatBrief`) | nenhum |
| `livros_afiliado.py` | 44 | nenhuma | `pipeline/affiliate.py` | nenhum |
| `checagem_local.py` | 85 | só o relatório | `pipeline/checagem_local.py` | nenhum |
| `teste_voz_gemini.py` | 161 | chama a API do Gemini por `urllib`, sem o adapter | `probe` | nenhum |
| `sprites_apresentador.py` | 254 | tudo (corte da folha, encaixe, máscaras, chroma) em numpy | nada | `test_sprites_apresentador.py` |
| `clipe_tempos.py` | 140 | tudo (letra do MP3 × palavras reconhecidas) | nada | nenhum |
| `clipe_reconhecer.py` | 70 | tudo (Whisper local em janelas) | nada | nenhum |

Três grupos saem daí:

- **A. Casca fina (≈ 880 linhas):** `metricas`, `livros_afiliado`, `radar_resumo`, `formato_resumo`, `conferir_audio`,
  `evolucao`, `catalogo_musica`, `checagem_local`. A lógica já está em `app/`; virar comando é escrever
  `add_arguments` e `run` em `app/commands/`, sem lógica nova.
- **B. Lógica presa no script (≈ 1.240 linhas):** `montar_episodio`, `shorts_tec`, `buscar_candidatos`,
  `baixar_escolhidos`, `baixar_fonte`, `fonte_declarada`. Pedem módulo novo em `app/pipeline/` ou `app/media/`
  e o comando por cima. Os cinco testes que hoje carregam o script por caminho (`spec_from_file_location`)
  passam a importar de `app/`.
- **C. Fora do fluxo do episódio (≈ 625 linhas):** `clipe_reconhecer`, `clipe_tempos`, `sprites_apresentador`,
  `teste_voz_gemini`. Não viram `vp`: são ferramenta de uma vez ou benchmark superado.

## 3. Como o `vp` ficaria

Comandos novos ou preenchidos, na ordem do fluxo. "Pré-requisito" é o que o comando confere antes de agir
(proposta; a decisão é do dono, §7). "Rede" segue o §14: só com pedido do dono na sessão.

| Comando | Subcomandos | Vem de | Módulo do comando | Lógica | Portas do `Context` | Rede | Pré-requisito | Issue |
|---|---|---|---|---|---|---|---|---|
| `vp sources` | `add <id> <url> --title --kind [...]`, `declare <id> <arquivo> --title` | `baixar_fonte`, `fonte_declarada` | `app/commands/sources.py` | `app/pipeline/sources.py`: `next_source_id`, `register_source` (raw, txt, trechos, `sources.json`), `fetch` separado | `store` | `add`: sim | nenhum; o gate 1 vem depois | #26 |
| `vp brief` | `radar <id> <nicho>`, `formato <id> <arquivo>` | `radar_resumo`, `formato_resumo` | `app/commands/brief.py` | `app/pipeline/briefs.py`: uma só `place_dated_copy(target, text, parse, kept_name)` | `store` | não | nenhum | ADR 018, 031 |
| `vp assets` | `buscar <id> pedidos.json [--limit]`, `baixar <id> <cena> <asset-id>...` | `buscar_candidatos`, `baixar_escolhidos` | `app/commands/assets.py` | `app/pipeline/assets.py`: `search_candidates`, `write_candidates`, `download_chosen` | `archives`, `store` | sim (bancos) | plano de imagens validado pelo dono (regra da skill) | #22, #19 |
| `vp music` | `add <arquivo> --titulo ...`, `use <id> <faixa>`, `list` | `catalogo_musica` | `app/commands/music.py` | `app/pipeline/music.py` ganha `add_track` e `copy_to_episode` | `store` | não | `use`: antes do gate 3 da faixa | ADR 030 |
| `vp voice` | `<id> [--final] [--voz=<nome>]` | `montar_episodio` | handler em `app/cli.py` | `app/pipeline/production.py` | `tts`, `tts_final`, `tts_named`, `store` | `--final`, `gemini`, `chatterbox_modal`: sim | rascunho: `vp check` sem erro; `--final`: gate 2 válido (proposta) | #16 |
| `vp subs` | `<id> [--palavra]` | `montar_episodio` | idem | `production.py` sobre `captions` e `word_captions` | `word_aligner` | `--palavra`: sim (Groq) | WAVs prontos | #17 |
| `vp render` | `<id> [--preview]` | `montar_episodio` | idem | `production.py` | `renderer(format)` | não | prévia: `episode.json`; final: gate 2 válido e ativos usados aprovados (proposta) | #13 |
| `vp short` | `voz`, `tempos`, `sfx`, `juntar`, `boca`, `gate` | `shorts_tec` | `app/commands/short.py` | `app/pipeline/short.py` (narração, nomes dos WAVs, tempos, começos de cena, pasta de gate) e `app/media/mix.py` (silêncios das pontas, filtro de mistura, junção) | `tts_final`, `tts_named`, `settings` | `voz`: sim (Modal) | `gate`: `vp medicao` limpo (já é regra do gate 4) | ADR 033, 035, 036 |
| `vp audio` | `<mp4> (--episodio=<id> \| --content=<json>) [--sfx=<json>]` | `conferir_audio` | `app/commands/audio.py` | `app/media/earshot.py` ganha `cuts_from_episode`, `cuts_from_content`, `expected_from_sfx` | `settings.earshot` | não (processo local) | sonda de CPU | ADR 035 |
| `vp evolucao` | `gerar`, `guardar`, `comparar`, `lado-a-lado` | `evolucao` | `app/commands/evolucao.py` | `app/media/evolution.py`; `gerar` chama `production.produce(preview=True, voice="gemini")` em vez de subprocesso | `renderer`, `tts_named` | `gerar`: sim (Gemini) | autorização do dono para o vídeo-régua | #69 |
| `vp metricas` | `iniciar`, `ler`, `pendentes`, `tabela` | `metricas` | `app/commands/metricas.py` | `app/pipeline/metrics.py` (já pronto) | `settings.data_dir` | não | publicado | §12 |
| `vp export` | `<id>` | `livros_afiliado` (primeira fatia) | handler | `affiliate.py`; `credits.txt` a partir dos ativos ainda não existe (`attribution.py` é só o rodapé dos planos) | `store` | não | gate 4 | #18 |

Fora do `vp`: `checagem_local.py` e `teste_voz_gemini.py` vão para `scripts/bench/` (medição, não etapa);
`sprites_apresentador.py`, `clipe_tempos.py` e `clipe_reconhecer.py` para uma pasta de ferramentas de uma vez
(nome a decidir). `scripts/provisorio/` deixa de existir.

Resultado: 13 scripts viram 12 comandos (6 novos: `brief`, `music`, `short`, `audio`, `evolucao`, `metricas`;
6 placeholders do `--help` preenchidos: `sources`, `assets`, `voice`, `subs`, `render`, `export`), e 5 ficam
scripts, em pasta nomeada pelo que são.

## 4. O que muda na estrutura do `app/`

1. **Registro único de comandos.** Hoje `build_parser()` e `main()` tratam `postiz` e `usage` à parte (dois
   `if`, uma exceção de configuração por nome). `Command` ganha um campo `module` (com `add_arguments`, `run` e
   `report_error`), `HANDLERS` sai do módulo, e `main()` trata todos iguais. É o pré-requisito de todos os PRs
   abaixo e não muda nada para quem usa.
2. **`Context` completo.** `app/pipeline/ports.py` não declara `tts_final`, `tts_named(name)` nem
   `word_aligner`; o `LazyContext` já os tem, o `FakeContext` de `tests/fakes/` não. Entram na porta e no fake.
3. **Chave da voz na porta TTS.** O `montar_episodio.py` importa `reference_hash` e `MAX_PART_CHARS` do adapter
   Chatterbox e lê `settings.gemini_tts`, `kokoro` e `chatterbox` pelo nome do provedor. Em `app/pipeline/` isso
   é proibido (`tests/test_architecture.py`). Proposta: `TTSProvider.fingerprint(language) -> str` (o que muda a
   fala além do texto: modelo, voz, referência, parâmetros efetivos da entrega, corte em frases). Cada adapter
   responde por si, e o Chatterbox inclui `exaggeration` e `cfg_weight` da entrega, o que fecha o #190 (G5).
   A chave do WAV vira `sha256(fingerprint | entrega | texto com glossário)`; `pause_ms` entra no fingerprint
   de quem faz silêncio.
4. **`app/pipeline/production.py`** (nome da #193): `produce(context, episode_id, *, final, voice, preview,
   render, word_captions, now) -> ProductionReport`. Etapas `voice`, `subs` e `render` passam por `run_step`
   (lock, estado, falha registrada, reuso por `input_hash`); `episode.json` sai por `write_output` (recusa
   etapa aprovada); o motor vem de `context.renderer(format)`. O `run_step` já trava o episódio: `produce` não
   trava por fora (#193). WAV novo é gerado em temporário e promovido depois do `duration_ms` (#188). Os
   segmentos atômicos do Remotion (#189) são do motor, fora deste mapa.
5. **`app/media/mix.py`** (`speech_bounds`, `bounds_from_log`, `mix_filter`, `mix`) e **`app/pipeline/short.py`**
   (`Line`, `load_lines`, `wav_name`, `fit_durations`, `scene_starts`, `voiced`, `sfx_placed`, `gate_folder`).
   O `conferir_audio.py` deixa de importar do `shorts_tec.py`.
6. **`app/pipeline/sources.py`** e **`app/pipeline/assets.py`**, como na tabela. O `assets` depende de a porta
   `archives` tolerar banco sem chave: hoje `LazyContext.archives` lança `ConfigurationError` no primeiro nome
   sem fábrica ou sem chave, e o script contorna lendo o `DEFAULT_REGISTRY`. Proposta: `archives` devolve os
   montáveis e `archives_skipped` os motivos, impressos antes da busca (#192).
7. **Testes.** `test_chatterbox_tts.py`, `test_narration.py`, `test_metrics.py`, `test_shorts_tec.py` e
   `test_sfx.py` trocam `spec_from_file_location` por import de `app/`. `test_architecture.py` passa a cobrir os
   módulos novos sem mudança.
8. **Fora do código.** Citam scripts e mudam no mesmo PR de cada comando: skills `pauta`, `plano-de-imagens`,
   `trilha`, `vp-trilha`, `shorts-tec`, `short-diario`, `analise-de-formato` (SKILL.md e `brief.py`), agente
   `diretor-musical`, CLAUDE.md (§1, mapa do §3, §4, §6, §9, §10, §15: 8 linhas), `docs/diagramas/mermaid/pipeline-hoje.mermaid`,
   `data/benchmarks/evolucao-template.md` (cabeçalho gerado por `app/media/evolution.py`). As ADRs ficam como
   estão (histórico). `.claude/settings.local.json` libera `shorts_tec.py` e `conferir_audio.py` por caminho: o
   dono troca para `.venv/bin/vp short *` e `.venv/bin/vp audio *` (a pasta `.claude/` está na lista de negação
   do agente).

## 5. Desenho em objetos

O `app/` já tem um estilo: **porta** é um `Protocol` (`TTSProvider`, `ArchiveProvider`, `ManifestStore`,
`RenderEngine`, `Context`); **adapter** é uma classe com `info`, uma por provedor; **valor** é
`dataclass(frozen=True)` ou modelo pydantic quando vai para arquivo; a **lógica** de `app/pipeline/` e `app/media/`
é função sobre valores. Classe com estado aparece onde há um recurso com ciclo de vida: a pasta de JSON
(`JsonFileStore`), o processo da voz clonada (`ChatterboxTTS.close`), o contexto preguiçoso (`LazyContext`). O
desenho abaixo segue essa regra: classe onde há estado ou recurso, valor para o que atravessa etapas, função
para transformação pura. Nada de classe por cerimônia.

### 5.1 O que nos scripts é procedural

- `main()` de cem linhas misturando política (o que regenerar), caminhos e chamadas a provedor
  (`montar_episodio`, `shorts_tec`).
- O layout da pasta do episódio reescrito em cada script (`data_dir / "episodes" / id / "voice"`, `"assets"`,
  `"renders"`, `"candidatos"`, `"sources/raw"`). Em `app/` são 20 constantes de nome de arquivo em 14 módulos e
  nenhum objeto que as reúna.
- O cache de voz (nome do WAV, chave, apagar o antigo, gerar o que falta) escrito duas vezes, com regras
  diferentes: o longo não põe o idioma no nome; o Short põe porque gerar um idioma apagava o outro.
- Dicionários soltos atravessando etapas: `pedidos.json`, `candidatos/*.json`, `narracao.json`, `*.voz.json` e o
  JSON do motion-video (lido por `scene["durationSec"]` em quatro funções). O `narracao.json` já tem modelo em
  `app/pipeline/translation.py` (`Narration`, `NarrationLine`); o `shorts_tec.py` reinventa `Line`.
- Conhecimento de provedor no orquestrador: `voice_fingerprint`, `CLONED`, `BATCH_CHARS`, `synthesize_many`
  descoberto por `getattr`, `reference_hash` e `MAX_PART_CHARS` importados do adapter.
- Efeitos sem fronteira: o WAV antigo é apagado antes de gerar o novo (#188); `episode.json` escrito direto, sem
  lock nem estado (#193); `sys.argv` lido dentro de `word_captions`.

### 5.2 Os objetos

| Objeto | Natureza | Responsabilidade | Substitui |
|---|---|---|---|
| `EpisodeFolder` (`app/pipeline/episode.py`) | objeto sobre `ManifestStore` e o id | sabe os nomes e as pastas do episódio: `scenes()`, `sources()`, `music_plan()`, `glossary()`, `media(asset_id)`, `track(asset_id)`, `voice_dir`, `renders`, `candidates`, `stage_final(mp4, texto)`; escreve por `write_output` | os `data_dir / "episodes" / id / ...` dos 14 scripts e, aos poucos, as 20 constantes |
| `VoiceKey` (`app/pipeline/voice.py`) | valor | provedor, idioma, impressão digital, entrega, texto lido; `digest` e `stem(scene_id)`: o esquema de nome do WAV num lugar só | a chave montada à mão no `montar` e o `wav_name` do `shorts_tec` |
| `VoiceLibrary` | objeto sobre a pasta `voice/` | `wav(key)`, `exists`, `stale(scene, provider, idioma)`, `promote(tmp)`, `prune()`: só arquivos, nenhum provedor | os laços de `glob` e `unlink` dos dois scripts |
| `Narrator` | objeto com ciclo de vida (`with`) sobre `TTSProvider`, `VoiceLibrary` e glossário | `plan(lines)` devolve o que falta; `synthesize(requests) -> list[SceneOutcome[Path]]`: lote se o provedor oferece, cena a cena na recusa, falha de provedor para a cena e não o episódio (§2.1, `failures.py`); `close()` | `batches`, `generate`, `cmd_voz`, o `getattr(tts, "close")` |
| `SpeechLine` | valor (`id`, `text`, `delivery`) | o que o `Narrator` recebe; o longo monta de `ScenesManifest`, o Short de `Narration` | `Line` |
| `Production` (`production.py`) | serviço com estado entre etapas (`context`, `folder`, `options`, provedor escolhido, WAVs, manifesto) | `voice()`, `captions()`, `episode()`, `render()`, `run()`; cada etapa passa por `run_step`; `ProductionOptions` e `ProductionReport` são valores | o `main()` do `montar_episodio` |
| `assemble_episode(...)` | função | cenas, duração de cada WAV, rodapé e trilha → `EpisodeManifest` v2; a duração entra injetada (`duration: Callable[[Path], int]`) | o laço do `cursor` no `montar` |
| `Narration`, `NarrationLine` | valor pydantic, já existe em `translation.py` | `narracao.json`; vai para `short.py` e o `translation` importa de lá | `Line`, `load_lines` |
| `VoicedNarration`, `VoicedLine` | valor pydantic | `<narracao>.voz.json`: o que `voz` entrega a `tempos`, `juntar` e `boca` (`wav`, `seconds`, `speech`) | o dicionário gravado por `cmd_voz` e relido por `voiced` |
| `MotionContent` | objeto sobre o JSON do motion-video, só o que o auto-play toca (`fps`, `scenes[].id`, `durationSec`, `type`, `host`) | `starts()`, `durations()`, `fitted(seconds, pad) -> MotionContent` (devolve novo, não altera no lugar), `save(path)` | `scene_starts`, `fit_durations` e as releituras do dicionário em `juntar`, `sfx`, `boca` e `conferir_audio` |
| `SpeechSpan` | valor (`wav`, `begin`, `end`) | a fala dentro do WAV; `speech_bounds(path)` fica função (ffmpeg, sem estado) | `Speech` do `shorts_tec` e `Speech(seconds)` do `sfx.py`, hoje com o mesmo nome |
| `AudioMix` (`app/media/mix.py`) | construtor (builder) | `.speech(wav, at_ms, span)`, `.effect(file, at_ms, trim_s, gain_db)`, `.video_audio(bool)`, `.filter()` (a string, testável como hoje), `.render(out) -> MixResult(lufs, problem)` | `mix_filter` e o corpo de `cmd_juntar` |
| `ShortProduction` (`short.py`) | serviço, espelho da `Production` | `voice()`, `fit()`, `check_sfx()`, `join()`, `mouth()`; compõe `Narrator`, `VoiceLibrary`, `MotionContent`, `AudioMix` e `sfx.py`; sem herança com `Production`: os dois compartilham componentes, não uma classe base | os seis `cmd_*` |
| `SourceDraft`, `Extracted` | valores | o que o dono informa (título, url, tipo, autores, interesse, notas) e o que a extração devolve (bruto, sufixo, parágrafos); `fetch_url`, `from_file` e `declared` são três funções que devolvem `Extracted` | os argumentos soltos e o `pdftotext` em linha |
| `SourceRegistry` | objeto sobre `EpisodeFolder` | `next_id()`, `register(draft, extracted, now) -> Source`: bruto, txt, trechos e `sources.json` pelo store (atômico; recusa se o gate 1 carimbou) | as 30 linhas duplicadas em `baixar_fonte` e `fonte_declarada` |
| `CandidateRequest`, `CandidateRecord`, `CandidateSet`, `SearchFailure` | valores pydantic | `pedidos.json` e `candidatos/<pedido>.json` com schema | os dicionários `pedido`, `_record` e `records[...]["ativo"]["id"]` |
| `CandidateSearch` | serviço sobre `Sequence[ArchiveProvider]` | `run(request, orientation, limit) -> CandidateSet`; falha de um banco vira `SearchFailure` e não interrompe (§2.1) | o laço triplo de `buscar_candidatos` |
| `CandidateIndex` | objeto sobre a pasta `candidatos/` | `save(set)`, `load_all()`, `by_asset_id()` | a leitura por `glob` em `baixar_escolhidos` |
| `AssetIntake` | serviço sobre os adapters por provedor | `take(record, scene_id) -> Asset`: baixa, `sha256`, `assets/<id>.json` em `needs_review` | o `main` de `baixar_escolhidos` |
| `ArchiveCascade` | valor (`available`, `skipped` com nome e motivo) | o que o `Context` devolve em vez de quebrar no primeiro banco sem chave (#192) | `available_archives` lendo o `DEFAULT_REGISTRY` |
| `MusicLibrary`, `TrackDraft` | objeto sobre `data/music/` e valor | `tracks`, `add(file, draft, now) -> MusicTrack`, `copy_to(folder, asset_id)`; `load_music_catalog` continua para o `vp check` | `add`, `use`, `list_tracks` |
| `EpisodeBrief[T]` (`briefs.py`) | objeto genérico (pasta, nome do arquivo, modelo, nome do guardado, resumo) | `place(text, replace) -> Placement` (igual, colocado, trocado); duas instâncias, radar e formato | os dois scripts de cópia datada |
| `Earshot` (`app/media/earshot.py`) | objeto de configuração (`python`, `threads`), como um adapter | `timeline(media, cuts, out) -> Review`; `AudioReviewPlan(cuts, expected)` é valor montado de `EpisodeManifest` ou de `MotionContent` mais o `sfx` | `run_timeline(python, ...)` com a configuração passada a cada chamada |
| `TemplateSnapshot` | valor (`commit`, `template_hash`, `motion_kit`) com `from_worktree` e `from_ref` | o que a versão do vídeo-régua registra | `template_info`, `project_info` |

### 5.3 O que muda nas portas

- `TTSProvider.fingerprint(language) -> str`: cada adapter diz o que muda a fala dele além do texto. Kokoro:
  voz e `pause_ms`; Gemini: modelo, voz e estilo; Chatterbox: modelo, idioma, hash da referência, `pause_ms`,
  parâmetros efetivos da entrega e o corte em frases. Fecha o #190 e tira do orquestrador `CLONED`,
  `voice_fingerprint` e `long_speech_tag`.
- `BatchTTS` (`Protocol` com `runtime_checkable`): `synthesize_many(requests)` e `max_batch_chars`. O `Narrator`
  agrupa só quando `isinstance(tts, BatchTTS)`. Hoje é `getattr` e `BATCH_CHARS` fixo no script.
- `Closeable`: `close()`; o `Narrator` é `with`.
- `Context`: `tts_final`, `tts_named` e `word_aligner` declarados; `archives` passa a devolver `ArchiveCascade`,
  ou ganha um `archive_cascade()` ao lado para não mudar a assinatura.
- `FakeTTS`, `FakeArchive` e `FakeContext` acompanham. Fora de `tests/fakes/` nenhum teste existente muda.

### 5.4 Dependências

```
app/commands/*               argparse → serviço (sem lógica)
app/pipeline/production.py   Production, ProductionOptions, ProductionReport, assemble_episode()
app/pipeline/short.py        ShortProduction, Narration, VoicedNarration, MotionContent
app/pipeline/voice.py        VoiceKey, VoiceLibrary, Narrator, SpeechLine        <- os dois acima
app/pipeline/episode.py      EpisodeFolder                                        <- todos
app/pipeline/sources.py      SourceDraft, Extracted, SourceRegistry, fetch_url, from_file, declared
app/pipeline/assets.py       CandidateRequest/Record/Set, CandidateSearch, CandidateIndex, AssetIntake
app/pipeline/music.py        + MusicLibrary, TrackDraft
app/pipeline/briefs.py       EpisodeBrief[T]
app/media/mix.py             AudioMix, MixResult, speech_bounds()
app/media/earshot.py         + Earshot, AudioReviewPlan
app/providers/tts/base.py    + fingerprint, BatchTTS, Closeable
```

Tudo em `app/pipeline/` continua dependendo só de portas e valores (`test_architecture.py`); os adapters
implementam os métodos novos; `bootstrap.py` não ganha classe nova, só as fábricas de sempre.

### 5.5 O que fica função, de propósito

`shots.py`, `captions.py`, `word_captions.py`, `narration.py`, `pauses.py`, `sfx.py`, `loudness.py`, `probe.py`,
`affiliate.py`, `metrics.py`, `numbers.py` e `evolution.py`: transformação pura ou uma chamada de I/O, já
testados com fakes. Classe em cima seria cerimônia. `Production` e `ShortProduction` os chamam.

### 5.6 Por onde provar o desenho

`VoiceKey`, `VoiceLibrary` e `Narrator` são o pedaço com mais duplicação e mais testes já escritos
(`test_chatterbox_tts`, `test_narration`, `test_shorts_tec`). O PR 5a extrai os três com esses testes migrados, e o
`montar_episodio.py` e o `shorts_tec.py` passam a usá-los sem mudar comportamento. Se o desenho não couber aí,
descobre-se antes do resto.

## 6. Ordem proposta (um PR por etapa, com calma)

| PR | O quê | Scripts que somem | Issues |
|---|---|---|---|
| 0 | Registro único de comandos; `Context` e `FakeContext` com `tts_final`, `tts_named`, `word_aligner` | nenhum | #192 (parte) |
| 1 | `vp metricas` e `vp brief radar\|formato` | 3 | — |
| 2 | `vp music` e `vp audio` | 2 | ADR 030, 035 |
| 3 | `vp sources add\|declare` | 2 | #26 |
| 4 | `vp assets buscar\|baixar` com a porta `archives` tolerante | 2 | #22, #192 |
| 5a | `voice.py` (`VoiceKey`, `VoiceLibrary`, `Narrator`) e `production.py` extraídos; os dois scripts viram casca; testes migram; comportamento igual (a folha de quadros do vídeo-régua prova que nada mudou, com autorização do dono) | nenhum | #193 (parte) |
| 5b | `fingerprint`, `BatchTTS` e `Closeable` na porta TTS; WAV preservado | nenhum | #190, #188 |
| 5c | `vp voice`, `vp subs`, `vp render` pela `Production` com `run_step`, gates e `context.renderer`; `vp evolucao` | 2 | #13, #16, #17, #193, #69 |
| 6 | `vp short` pela `ShortProduction` (`MotionContent`, `AudioMix`, `VoicedNarration`); skills e allowlist | 1 | ADR 033, 035, 036 |
| 7 | `vp export` primeira fatia (livros e `credits.txt`) | 1 | #18 |
| 8 | `scripts/bench/` e a pasta de ferramentas; `scripts/provisorio/` some; CLAUDE.md §10 e mapa | 5 movidos | — |

Nenhum destes PRs muda template ou motion-kit: não geram versão nova do vídeo-régua, salvo a prova do 5a.

## 7. Riscos e o que não entra

- A rotina diária (ADR 036) e a skill `short-diario` dependem do `shorts_tec.py` e do `conferir_audio.py` pelos
  nomes atuais: o PR 6 troca a skill e a allowlist no mesmo commit, e o dono confere a rotina uma vez depois.
- `vp voice --final` e `vp subs --palavra` chamam serviço remoto (Modal, Groq): o comando imprime o provedor e o
  `remote` antes de chamar, e a regra do §14 (pedido do dono na sessão) continua fora do código.
- Não entra aqui: `vp new`, `vp reopen`, `vp script`, `vp scenes`, `vp gallery` (sem script provisório que os
  cubra; `script` e `scenes` são dos agentes desde a ADR 009), a tradução do longo (ADR 034), os eventos de cena
  no motion-kit e a música no Short (lacunas de `pipeline-hoje.mermaid`).

## 8. Questões em aberto (decisão do dono)

1. **Nomes.** `vp short`, `vp brief`, `vp audio`, `vp music` (como `check`, `status`, `sources`) ou em português
   (`vp trilha`, `vp musica`, como `checagem`, `medicao`, `numeros`)? Recomendação: o nome do arquivo ou do
   conceito que o CLAUDE.md já usa (`music.json` → `music`; `metricas`, `evolucao` como os scripts).
2. **Produção.** Três comandos (`voice`, `subs`, `render`, como o `--help` promete desde o roadmap) ou um só
   `vp montar <id>` que faz tudo, como o script? Recomendação: os três, sem encadear, porque os pré-requisitos
   diferem (voz de rascunho antes do gate 2, render final depois).
3. **Pré-requisitos.** Rascunho (Kokoro, prévia) sem gate; `--final` e render final exigem gate 2 válido e os
   ativos usados aprovados, com `--sem-gate "motivo"` gravado no `review.json` como o `--sem-checagem` do
   `approve`? Recomendação: sim, numa ADR curta (emenda da ADR 009).
4. **Os cinco que ficam scripts.** Guardar em `scripts/bench/` e numa pasta de ferramentas, ou apagar os dois
   benchmarks já superados? Recomendação: guardar, porque o CLAUDE.md §15 e `data/benchmarks/` os citam.
5. **Ordem.** Pequenos primeiro (PRs 0–4) para firmar o padrão, ou a produção (5) primeiro por ser o maior ganho?
   Recomendação: PR 0 e PR 1 primeiro, que cabem numa sessão e provam o padrão sem risco.

Sobre o desenho em objetos (§5):

6. **`EpisodeFolder`** como o único objeto que sabe os nomes de arquivo: entra de uma vez ou aos poucos (código
   novo usa; as funções antigas de `app/media/` seguem recebendo `Path`)? Recomendação: aos poucos.
7. **Nome do WAV do longo** com o idioma, como no Short: regenera o cache dos episódios em produção (custo no
   Modal) ou renomeia uma vez? Recomendação: `VoiceKey.stem` mantém o esquema antigo no longo até uma migração
   marcada; é uma linha num lugar só, de qualquer jeito.
8. **`Production` e `ShortProduction`** como classe, ou `produce()` como função? Recomendação: classe, pelo
   estado entre etapas e pelo `with` do processo da voz clonada.
9. **Portas novas** (`fingerprint`, `BatchTTS`, `Closeable`, `ArchiveCascade`): uma ADR curta ou emenda da ADR 006?
   Recomendação: uma ADR nova, "porta TTS e cascata de acervos", porque muda o contrato que todo adapter cumpre.
