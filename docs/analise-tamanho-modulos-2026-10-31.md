# Gate de tamanho em `app/` e as refatorações que ele pede (2026-10-31)

Pedido do dono: um gate para os arquivos de `app/` com no máximo 50 linhas, pelo S do SOLID (uma
responsabilidade por módulo), e a análise das refatorações necessárias. O gate está em
`tests/test_tamanho_modulos.py` (roda no `pytest`, no CI e no pré-commit); este documento registra a medida de
hoje, o que o limite implica e como cada arquivo se partiria. Medido na árvore local em 2026-10-31.

**Regra vigente:** 200 linhas de código por arquivo e 50 por função, com 13 arquivos e 10 funções na
baseline inicial. O pedido de 50 por arquivo é o histórico analisado abaixo. A sequência de trabalho está no
[fluxo de refatoração com gates](fluxo-refatoracao-solid-2026-11-01.md).

## 1. A medida de hoje

"Linha de código" é a que tem algum token fora de branco, comentário e docstring: documentar, que é estilo da
casa (docstring de módulo explicando a decisão), não conta contra o limite.

| Medida | Valor |
|---|---|
| Arquivos `.py` em `app/` (com código) | 81 (68) |
| Linhas físicas / de código | 12.649 / 9.638 |
| Mediana / máximo de linhas de código por arquivo | 66 / 1.155 (`schemas.py`) |
| Arquivos acima de 50 linhas de código | 49 |
| Acima de 100 / 150 / 200 / 300 | 32 / 22 / 13 / 6 |
| Funções ou métodos acima de 50 linhas de código | 10 |
| Funções com complexidade ciclomática acima de 10 (`ruff C901`) | 13 (5 coincidem com as dez acima) |
| Funções com mais de 50 comandos (`ruff PLR0915`) | 0 |
| Classes acima de 50 linhas | `SQLiteUsageLedger` 306, `RemotionEngine` 226, `PostizClient` 181, `FfmpegEngine` 167, `StockArchive` 112, `ChatterboxTTS` 88, `Asset` 77, `LazyContext` 74, `EpisodeManifest` 58 |

As dez funções acima de 50 linhas de código, em ordem:

| Linhas | Função | Complexidade |
|---|---|---|
| 73 | `pipeline/check.py::_check_scenes` | 18 |
| 68 | `pipeline/molde.py::molde_warnings` | 16 |
| 68 | `render/remotion.py::RemotionEngine.scene_props` | 15 |
| 62 | `commands/usage.py::run` | 14 |
| 54 | `commands/postiz_cadeia.py::build_package` | — |
| 54 | `pipeline/bench.py::run_bench` | — |
| 53 | `pipeline/sfx.py::plan_problems` | 13 |
| 52 | `pipeline/gates.py::record_decision` | — |
| 51 | `pipeline/numbers.py::render_block` | — |
| 51 | `render/ffmpeg.py::FfmpegEngine._render_segment` | — |

Complexas sem passar de 50 linhas: `schemas.py::Asset._approval_requires_rights` (22), `text_fit_warnings` (17),
`schemas.py::_ordered_timeline` (16), `music.py::plan_problems` (14), `commands/postiz.py::run` (14),
`check.py::variety_warnings` (12), `radar.py::_measured` (12), `postiz_validation.py::validate_schedule` (12).

## 2. O gate

`tests/test_tamanho_modulos.py`, com dois limites: `MAX_CODE_LINES_PER_FILE = 200` e
`MAX_CODE_LINES_PER_FUNCTION = 50`. É uma catraca: o que hoje passa do limite está em
`tests/baseline_tamanho_app.json` (13 arquivos e 10 funções na baseline inicial) e só pode encolher.

- Arquivo ou função nova acima do limite: falha.
- Entrada da baseline que cresceu: falha ("só encolhe").
- Entrada da baseline que já cabe no limite ou não existe mais: falha, pedindo para tirá-la (a catraca aperta).
- Regenerar a baseline, só quando um PR encolheu ou dividiu algo:
  `uv run python tests/test_tamanho_modulos.py --baseline`. O diff do JSON mostra no PR o que encolheu.
- Roda em três lugares: `uv run pytest` (CI), o pré-commit (`.githooks/pre-commit`, em modo gate, sem
  pytest) e à mão, sem argumento.

Mudar um limite é uma linha; a baseline se regenera com um comando. O gate não decide o limite certo: o §3 e o
§4 decidem.

## 3. O que o limite de 50 por arquivo implica

Três leituras do mesmo pedido, com o que cada uma custa:

| Regra | Falha hoje | O que mede | Custo para cumprir |
|---|---|---|---|
| **50 linhas de código por arquivo** (o pedido) | 49 arquivos | tamanho do módulo | 9.638 linhas em arquivos de 50 dão no mínimo 193 arquivos; com cabeçalho (imports) uns 230, quase três vezes os 81 de hoje. Nove classes passam de 50 sozinhas: cumprir o limite exige parti-las em mixins ou delegados, o que não é separar responsabilidade, é espalhar uma. |
| **50 por função e complexidade até 10** | 10 funções + 13 complexas (18 distintas) | responsabilidade onde ela mora: a função que confere oito regras num laço | 18 extrações de função, sem mover arquivo |
| **200 por arquivo mais a regra acima** | 13 arquivos + 18 funções | módulo com várias responsabilidades | 13 partições em pacote (§4, grupo 1) mais as 18 extrações |

O S do SOLID fala de uma razão para mudar por unidade. Nos arquivos de `app/` a unidade que acumula razões é a
função grande (`_check_scenes` confere âncora, pausa, claim, tipo de plano e entrega no mesmo laço) e o módulo
que junta famílias de contratos (`schemas.py` tem 94 definições). O arquivo de 60 a 150 linhas com uma classe ou
um conjunto de funções sobre um só assunto (`shots.py`, `extract.py`, `json_files.py`) não acumula razões: parti-lo
só pelo número cria arquivos sem dar clareza.

## 4. As refatorações, arquivo por arquivo

Os 49 arquivos da baseline em três grupos. "Partição" é como o arquivo vira pacote ou módulos, pelo esqueleto
real (definições de topo e tamanho de cada uma). Importações de fora não mudam: cada pacote reexporta no
`__init__.py` o que o módulo de hoje exporta, e o `episode.json` (ADR 007) não muda de contrato por mover
classe de arquivo.

### Grupo 1: várias responsabilidades no mesmo arquivo (13 arquivos acima de 200 linhas)

| Arquivo | Código | Partição |
|---|---|---|
| `pipeline/schemas.py` | 1.155, 94 defs | pacote `pipeline/schemas/`: `base` (`Model`, `Status`, enums), `sources`, `facts`, `shots/` (um módulo por família: foto e B-roll; número e gráfico; citação e documento; mapa; linha do tempo; árvore; comparação; rede; palavra-chave; Reels com `hook`, `calculation`, `receipt`, `end_card`), `scenes` (`Scene`, `Objective`, `Funnel`, `Series`, `HostSpec`, `ScenesManifest`), `assets` (`Provider`, `Generation`, `Asset`; o validador `_approval_requires_rights`, complexidade 22, vira função em `rights.py`), `review` (`Step`, `Decision`, `ReviewEntry`, `ReviewLog`, `CheckEntry`, `CheckLog`), `music`, `episode` (`EpisodeFormat`, `VideoSpec`, `EpisodeShot`, `EpisodeScene`, `EpisodeMusic`, `EpisodeManifest`), `metrics`, `validation` (`unknown_source_refs`, `citation_violations`, `visual_need_violations`). Uns 14 módulos; `Asset` (77) e `EpisodeManifest` (58) continuam acima de 50 |
| `pipeline/check.py` | 577, 28 defs | pacote `pipeline/check/`: um módulo por `_check_*` que já existe (`sources`, `facts`, `scenes`, `numbers`, `variety`, `objective`, `funnel`, `radar`, `molde`, `music`, `metrics`) e `report.py` com `CheckReport` e `check_episode` (o orquestrador de 40 linhas). `_check_scenes` (73, complexidade 18) vira uma função por regra: âncoras, pausas, claims, tipos de plano, entrega |
| `cli.py` | 420, 32 defs | `app/commands/<grupo>.py` por comando (`decisions` com approve, reject, status e checagem; `check`; `numeros`; `bench`; `excerpts`; `conferencias` com medicao e traducao); `cli.py` fica com `Command`, `build_parser`, `main` e `project_root`. É o PR 0 de `docs/analise-scripts-provisorios-2026-10-31.md` |
| `render/ffmpeg.py` | 376 | pacote `render/ffmpeg/`: `engine` (`FfmpegEngine`), `segments` (`_render_segment`, `scene_image`, `frame_bounds`), `audio` (`audio_key`, `_encoded_audio`, `music_mix`, `_audio_parts`), `srt` (`Cue`, `parse_srt`, `cues_between`), `concat` (`assemble`, `_concat_list`, `_run`) |
| `storage/usage_sqlite.py` | 338, 1 classe de 13 métodos | o caso mais duro: uma classe que é o adapter inteiro. Partição por colaboradores que o ledger compõe: `schema.py` (DDL e migração), `budgets.py`, `runs.py`, `report.py`; `SQLiteUsageLedger` fica com a conexão e a transação. Ou aceitar a classe acima de 50 |
| `pipeline/numbers.py` | 334 | `timing` (`ShotTiming`, `scene_timings`, `shot_timings`, `rhythm_alert`, `image_changes`), `script_numbers` (`Citation`, `ScriptNumbers`, `script_numbers`, `niche_measures`), `format_brief` (`FormatMeasure`, `FormatBrief`, `format_warnings`), `outline_block` (`render_block`, `current_block`, `replace_block`, `strip_block`), `image_plan` (`render_image_plan`, `used_in_scenes_mismatches`) |
| `render/remotion.py` | 298, `RemotionEngine` 226 | `props.py` (`scene_props`, 68 linhas e complexidade 15, vira um construtor por tipo de plano; `_credit`, `_editorial`, `_host_identity`, `footage_continuity`), `engine.py` (render, segmentos, cache), `template.py` (`template_hash`, `region_codes`) |
| `pipeline/bench.py` | 295 | `machine` (`Machine`, `cpu_probe`, `read_machine`), `llm`, `tts`, `render`, `report` (`BenchReport`, `run_bench`, `summary`) |
| `media/evolution.py` | 268 | `versions` (`Sample`, `Version`, `store`, `load`, `versions`, `changed_shots`), `registry` (`registry_row`, `append_registry`, `_header`, `_row`), `sheet` (`contact_sheet`, `_fit`, `_text`, `_psnr`), `side_by_side` |
| `pipeline/molde.py` | 267 | `models` (`Molde` e filhas), `title` (`title_words`, `_title_said_at`, `_title_warnings`), `warnings` (`molde_warnings`, 68 linhas e complexidade 16, vira uma função por medida e uma tabela medida → função), `claims` (`claimless_statements`, `_proper_nouns`) |
| `pipeline/gates.py` | 256 | `hashes` (`gate_hash`, `content_hash`, `check_hash`, legados), `decisions` (`record_decision`, 52 linhas: uma função de pré-condição por gate; `record_check`), `report` (`GateStatus`, `gate_report`, `missing_pieces`) |
| `commands/postiz_cadeia.py` | 222 | `registro` (`append`, `read`, `record_upload`), `links` (`link_status`, `caption_links`, `link_findings`), `pacote` (`build_package`, 54 linhas: uma função por seção do pacote; `package`), `duvida` (`record_doubt`), `schedule` |
| `bootstrap.py` | 221 | pacote `app/bootstrap/`: `factories.py` (as fábricas, 4 a 10 linhas cada, agrupadas por porta), `registry.py` (`DEFAULT_REGISTRY`, `Registration`, `unknown_choices`), `context.py` (`LazyContext`), `__init__.py` (`build_context`, `build_postiz`, `build_usage`). O `test_architecture.py` confere o prefixo `app.bootstrap`; como pacote, continua valendo |

### Grupo 2: duas ou três responsabilidades, partição mecânica (18 arquivos de 100 a 200 linhas)

| Arquivo | Código | Partição |
|---|---|---|
| `media/captions.py` | 199 | `cues` (`Cue`, `Phrase`, `SceneAudio`, `phrases`, `scene_cues`, `episode_cues`, `_snap`), `srt` (`to_srt`, `parse_srt`, `timing_problems`, `review_hints`), `sync` (`captions_key`, `sync_captions`) |
| `providers/postiz.py` | 195, `PostizClient` 181 | transporte (`_request`, erros) e pontos de acesso (integrações, posts, upload, agendamento); ou aceitar a classe |
| `providers/tts/chatterbox.py` | 190 | `SubprocessWorker` vai para `chatterbox_worker.py`, que já existe; `split_long`, `_split_sentence`, `_pack`, `join_wavs` para `chatterbox_chunks.py`; `ChatterboxTTS` (88) fica |
| `pipeline/sfx.py` | 188 | `kit` (`SfxSound`, `SfxKit`, `load_kit`), `plan` (`SfxCue`, `SfxPlan`, `Speech`, `plan_problems`: uma função por verificação), `placement` (`PlacedSfx`, `resolve_sfx`) |
| `pipeline/state.py` | 182 | `model` (`StepState`, `EpisodeState`, `transition`, `plan`, `compute_input_hash`), `run` (`run_step`, `write_output`), `approval` (`approve_step`, `reopen_step`) |
| `settings.py` | 175 | `settings/models.py` (as classes de configuração) e `settings/load.py` (`read_dotenv`, `load_settings`, `speech_chars_per_second`) |
| `pipeline/checagem_local.py` | 166 | `cases` (`Case`, `build_cases`, mutações), `run` (`Veredito`, `Result`, `load_prompt`, `render`, `run`), `score` |
| `pipeline/translation.py` | 162 | `Narration` e `NarrationLine` vão para o módulo do Short (§5.2 da análise dos scripts); `spoken_numbers` e `_numeric_leaves` para `numbers_spoken.py`; ficam `TranslationLink` e os `*_problems` |
| `pipeline/radar.py` | 161 | `models` (`RadarBrief` e partes), `measures` (`_rates`, `_measured`, complexidade 12), `warnings` (`form_warnings`, `unmeasured_patterns`, resumos) |
| `providers/archives/stock.py` | 149 | `cache.py` (`ArchiveCache`) e `stock.py` (`StockArchive`, 112, fica) |
| `pipeline/format_decision.py` | 140 | `topic` (`TopicKind`, `TopicAssessment`, `decide_from_topic`) e `scenes` (`decide_from_scenes`, `_shot_class`); `FormatDecision` e `confirmed_format` ficam |
| `pipeline/music.py` | 137 | `catalog` (`load_music_catalog`), `plan` (`anchor_problems`, `plan_problems`, complexidade 14: uma função por verificação), `resolve` (`resolve_music`) |
| `pipeline/metrics.py` | 133 | `registry` (`ScheduledPost`, `scheduled_posts`), `readings` (`metrics_path`, `load`, `save`, `all_metrics`, `record_reading`, `pending_lines`, `summary_line`), `table` |
| `media/host.py` | 131 | `sprites` (`sprites_manifest`, `check_sprites`, `sprite_files`, `sprites_hash`) e `direction` (`blocked_corners`, `host_corners`, `host_direction`) |
| `providers/tts/gemini.py` | 126, uma classe | lote (`synthesize_many` e o corte nas pausas) separado da chamada; ou aceitar |
| `pipeline/medicao.py` | 123 | `numbers` (`screen_numbers`, `narration_numbers`) e `problems` (`entry_problems`, `coverage_problems`, `medicao_problems`) |
| `media/word_captions.py` | 120 | `match` (`CaptionWord`, `script_words`, `match_words`) e `sync` (`load`, `save`, `Report`, `sync_words`, `scene_word_frames`) |
| `commands/usage.py`, `providers/http.py` | 107, 101 | `usage.run` (62, complexidade 14) vira tabela subcomando → função; `http` separa `download` de `request` |

### Grupo 3: uma responsabilidade por arquivo, acima de 50 só pelo número (18 arquivos de 50 a 100 linhas)

`pipeline/shots.py` (91), `pipeline/bench_data.py` (86), `providers/postiz_validation.py` (83),
`providers/archives/pixabay.py` (80), `media/earshot.py` (79), `commands/postiz.py` (77), `pipeline/usage.py`
(74), `providers/text/ollama.py` (71), `pipeline/text_fit.py` (66), `providers/archives/pexels.py` (64),
`pipeline/extract.py` (60), `storage/json_files.py` (59: `JsonFileStore` e `JsonReviewGate`, dois arquivos se
preciso), `providers/tts/kokoro.py` (57), `media/pauses.py` (54), `providers/alignment/groq.py` (54),
`pipeline/ports.py` (53: um arquivo por porta, se preciso), `providers/archives/unsplash.py` (53),
`pipeline/affiliate.py` (50, no limite). Cada um é um adapter ou um conjunto de funções sobre um assunto. Partir
pelo número não separa responsabilidade; só aumenta a contagem de arquivos.

### As 18 funções

| Função | Extração |
|---|---|
| `check._check_scenes` (73, 18) | uma função por regra, cada uma `(scene, ...) -> list[str]`; `_check_scenes` só soma |
| `molde.molde_warnings` (68, 16) | uma função por medida; tabela `medida -> função` |
| `RemotionEngine.scene_props` (68, 15) | um construtor de props por tipo de plano; despacho por dicionário |
| `commands/usage.run` (62, 14) e `commands/postiz.run` (14) | tabela subcomando → função; o `match` de 7 braços some |
| `postiz_cadeia.build_package` (54) | uma função por seção do pacote (o quê, evidência, riscos, como desfazer) |
| `bench.run_bench` (54) | já delega a `bench_llm`, `bench_tts`, `bench_render`; sobra o laço e o relatório; separar a escrita do relatório |
| `sfx.plan_problems` (53, 13) e `music.plan_problems` (14) | uma função por verificação (âncora, cena, som, sobreposição) |
| `gates.record_decision` (52) | uma função de pré-condição por gate (`sources`, `script`, `assets`, `translation`, `preview`) |
| `numbers.render_block` (51) | um renderizador por seção do bloco |
| `FfmpegEngine._render_segment` (51) | construtor da cadeia de filtros separado da chamada ao ffmpeg |
| `Asset._approval_requires_rights` (22) | função em `rights.py` chamada pelo validador: uma regra por licença |
| `text_fit_warnings` (17), `_ordered_timeline` (16), `variety_warnings` (12), `radar._measured` (12), `validate_schedule` (12) | mesma receita: uma regra por função, a de cima só junta |

## 5. Recomendação inicial e decisão posterior

A recomendação inicial considerava 50 por arquivo, com catraca. A decisão posterior, ao fim desta seção,
fixou 200/50 e objetos primeiro. O raciocínio histórico para encolher a baseline era:

1. **Inspecionar as 18 funções** (§4, "as 18 funções"): tamanho e complexidade indicam onde examinar
   responsabilidades; extrair só quando separar uma regra coesa, com teste. Ligar `C901` no `ruff`
   (complexidade até 10) era uma proposta, não um gate já habilitado.
2. **Depois o grupo 1** (13 arquivos acima de 200), um por PR, na ordem em que outro trabalho já os toca:
   `cli.py` no PR 0 dos scripts provisórios; `schemas.py` quando entrarem os modelos de candidato e fonte;
   `check.py` quando entrar uma regra nova.
3. **O grupo 2 só quando a partição ajudar** quem está mexendo no arquivo; o grupo 3 fica na baseline.
4. **Rever o limite por arquivo depois do grupo 1.** Com 200 por arquivo e 50 por função, a baseline teria hoje
   13 arquivos e 10 funções em vez de 59 entradas, e o gate passaria a apontar só módulo com mais de uma
   responsabilidade.

**Decisão do dono (2026-10-31):** duas variáveis, 50 por função e 200 por arquivo; primeiro a orientação a objetos
(`docs/desenho-orientado-a-objetos-2026-10-31.md`), depois o aperto das linhas. Aplicada no mesmo dia: a baseline
ficou com 13 arquivos e 10 funções.

Pendente que não posso fazer daqui: uma linha no `CLAUDE.md` §14 citando o gate (o arquivo está na lista de
negação do agente).
