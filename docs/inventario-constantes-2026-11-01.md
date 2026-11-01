# Inventário de constantes — 2026-11-01

Escopo: `app/`. Regra e gate: [ADR 038](decisions/038-constantes-por-area.md) e
`tests/test_constants_layout.py`. São 311 constantes em 54 classes, com atributos `Final` e coleções
imutáveis. Nomes privados também estão incluídos. Os consumidores em testes e scripts foram atualizados.

| Área e arquivo | Classe | Constantes |
|---|---|---|
| [`app/commands/constants/cli_constants.py`](../app/commands/constants/cli_constants.py) | `CliConstants` | `EXIT_NOT_IMPLEMENTED`, `COMMANDS`, `DECISION_LABELS`, `CHECK_LABELS` |
| [`app/commands/constants/postiz_cadeia_constants.py`](../app/commands/constants/postiz_cadeia_constants.py) | `PostizCadeiaConstants` | `REGISTRO`, `UNDO`, `FIXED_RISKS`, `VERDICTS`, `NO_PACKAGE` |
| [`app/commands/constants/postiz_links_constants.py`](../app/commands/constants/postiz_links_constants.py) | `PostizLinksConstants` | `LINK`, `LINK_TIMEOUT_S`, `GONE` |
| [`app/media/constants/captions_constants.py`](../app/media/constants/captions_constants.py) | `CaptionsConstants` | `CAPTIONS`, `OLD_CAPTIONS`, `KEY`, `VERSION`, `MAX_CHARS`, `MIN_CUE_MS`, `SNAP_MS`, `PAUSE_SNAP_MS`, `END_SLACK_MS`, `_SENTENCE`, `_COMMA`, `_SRT_TIME`, `_WORD`, `_NUMBER_WORDS` |
| [`app/media/constants/earshot_constants.py`](../app/media/constants/earshot_constants.py) | `EarshotConstants` | `MAX_TRUE_PEAK_DBTP`, `SYNC_TOLERANCE_MS` |
| [`app/media/constants/envelope_constants.py`](../app/media/constants/envelope_constants.py) | `EnvelopeConstants` | `PERCENTILE` |
| [`app/media/constants/evolution_constants.py`](../app/media/constants/evolution_constants.py) | `EvolutionConstants` | `SAMPLE_AT`, `CELL_W`, `CELL_H`, `LABEL_W`, `HEADER_H`, `SIDE_W`, `SIDE_H`, `DURATION_TOLERANCE_MS`, `BACKGROUND`, `EMPTY`, `MARK`, `MARK_PX`, `CHANGE_PSNR_DB`, `VERSION`, `MOTION_KIT_SHA`, `MOTION_KIT_TARBALL`, `REGISTRY_COLUMNS`, `REGISTRY_HEADER` |
| [`app/media/constants/host_constants.py`](../app/media/constants/host_constants.py) | `HostConstants` | `SPRITES_DIR`, `VISEMES`, `ORIGIN_FILE`, `MANIFEST_FILE`, `KIT_CLI`, `POINT_SHOT_KINDS`, `POINT_MS`, `DELIVERY_EXPRESSIONS`, `GESTURE_CYCLE`, `GESTURE_EVERY` |
| [`app/media/constants/loudness_constants.py`](../app/media/constants/loudness_constants.py) | `LoudnessConstants` | `TARGET_LUFS`, `TOLERANCE_LU`, `_INTEGRATED`, `INTENSITY_STEPS` |
| [`app/media/constants/narration_constants.py`](../app/media/constants/narration_constants.py) | `NarrationConstants` | `PAUSE_TAG`, `LONG_PAUSE_TAG`, `PAUSE_CHARS`, `_PAUSE`, `_WELL_PLACED`, `_ANY_TAG` |
| [`app/media/constants/pauses_constants.py`](../app/media/constants/pauses_constants.py) | `PausesConstants` | `NOISE_DB`, `MIN_SILENCE_S`, `MIN_BOUNDARY_S`, `MARGIN`, `LEAD_S`, `TAIL_S` |
| [`app/media/constants/pronunciation_constants.py`](../app/media/constants/pronunciation_constants.py) | `PronunciationConstants` | `GLOSSARY_FILE` |
| [`app/media/constants/word_captions_constants.py`](../app/media/constants/word_captions_constants.py) | `WordCaptionsConstants` | `WORDS`, `VERSION` |
| [`app/pipeline/constants/affiliate_constants.py`](../app/pipeline/constants/affiliate_constants.py) | `AffiliateConstants` | `BOOKS_FILE`, `CHANNEL_FILE`, `AMAZON_HOSTS`, `DISCLOSURE`, `BLOCK_START`, `BLOCK_END` |
| [`app/pipeline/constants/attribution_constants.py`](../app/pipeline/constants/attribution_constants.py) | `AttributionConstants` | `MAX_LABELS`, `MAX_TITLE`, `INTERESTED_FLAG`, `_WORDS` |
| [`app/pipeline/constants/bench_constants.py`](../app/pipeline/constants/bench_constants.py) | `BenchConstants` | `BUSY_LOAD_PER_CPU`, `CPU_PROBE_SLOW_S`, `MAX_OUTPUT_TOKENS`, `RENDER_MODES` |
| [`app/pipeline/constants/bench_data_constants.py`](../app/pipeline/constants/bench_data_constants.py) | `BenchDataConstants` | `EXCERPTS`, `SYSTEM`, `NARRATION` |
| [`app/pipeline/constants/checagem_local_constants.py`](../app/pipeline/constants/checagem_local_constants.py) | `ChecagemLocalConstants` | `KINDS`, `PROMPT_FILE`, `_FICHA`, `_NUMBER`, `_WORD`, `SUPERLATIVE`, `EXPECTED` |
| [`app/pipeline/constants/check_constants.py`](../app/pipeline/constants/check_constants.py) | `CheckConstants` | `CHARS_PER_SECOND`, `MAX_GRAPHIC_RUN`, `MAX_STAMP_SHARE`, `MIN_SHOTS_FOR_SHARE`, `READING_MS`, `READING_KINDS`, `BAR_TYPES`, `BAR_PLAIN_BELOW`, `NEWS_MAX_AGE_DAYS`, `FUNNEL_ASKS`, `END_CARD_VARIANTS` |
| [`app/pipeline/constants/excerpts_constants.py`](../app/pipeline/constants/excerpts_constants.py) | `ExcerptsConstants` | `_BLANK_LINE`, `_ELISION`, `_TYPOGRAPHY` |
| [`app/pipeline/constants/extract_constants.py`](../app/pipeline/constants/extract_constants.py) | `ExtractConstants` | `BLOCKS`, `SKIPPED`, `_HYPHEN_BREAK`, `_CHARSET` |
| [`app/pipeline/constants/format_decision_constants.py`](../app/pipeline/constants/format_decision_constants.py) | `FormatDecisionConstants` | `PUBLIC_DOMAIN_CUTOFF_YEAR`, `EXPLAINER_GRAPHIC_SHARE`, `GRAPHIC_NEEDS`, `PHOTO_NEEDS` |
| [`app/pipeline/constants/gates_constants.py`](../app/pipeline/constants/gates_constants.py) | `GatesConstants` | `GATE_FILES`, `RENDERS`, `PREVIEW_FILES`, `AUDIO_SUFFIXES`, `CHECK_FILE`, `CHECKED_FILES`, `ASSET_ID`, `GATED_STEPS`, `MEDIA_SUFFIXES` |
| [`app/pipeline/constants/medicao_constants.py`](../app/pipeline/constants/medicao_constants.py) | `MedicaoConstants` | `MEDICAO_FILE`, `TEXT_KEYS`, `_NUMBER`, `DEFAULT_TOLERANCE` |
| [`app/pipeline/constants/metrics_constants.py`](../app/pipeline/constants/metrics_constants.py) | `MetricsConstants` | `EPISODES_DIR`, `PUBLICATIONS_DIR`, `REGISTRY_FILE`, `METRICS_DIR`, `TABLE_FILE`, `CSV_COLUMNS` |
| [`app/pipeline/constants/molde_constants.py`](../app/pipeline/constants/molde_constants.py) | `MoldeConstants` | `MOLDE_FILE`, `PARTITURA_FILE`, `OPENING_S`, `DURATION_TOLERANCE`, `CUT_RATIO`, `CLOSING_RISE`, `MIN_VIDEOS`, `STATEMENT_MIN_WORDS`, `TITLE_MIN_LETTERS`, `TITLE_STOP`, `_VOCE`, `_EU`, `_CONFISSAO`, `_SENTENCE_END`, `_WORD`, `_FIRST_PERSON`, `_STOP` |
| [`app/pipeline/constants/music_constants.py`](../app/pipeline/constants/music_constants.py) | `MusicConstants` | `MAX_BED_CHANGES_PER_MINUTE`, `MIN_CUE_MS` |
| [`app/pipeline/constants/numbers_constants.py`](../app/pipeline/constants/numbers_constants.py) | `NumbersConstants` | `MAX_SHOT_MS`, `LONG_KINDS`, `OPENING_SHARE`, `OPENING_S`, `BLOCK_START`, `BLOCK_END`, `FORMAT_FILE`, `IMAGE_PLAN_FILE`, `SPOKEN`, `MEASURE_LABELS` |
| [`app/pipeline/constants/radar_constants.py`](../app/pipeline/constants/radar_constants.py) | `RadarConstants` | `MEASURES`, `BRIEF_FILE`, `CAPTION_FILE`, `MAX_AGE_DAYS`, `OPENING_SHOTS`, `MIN_ANALYSED`, `_VIEWER`, `_SENTENCE_END`, `_EMOJI`, `_ASKS_COMMENT`, `PURPOSE_KINDS` |
| [`app/pipeline/constants/schemas_constants.py`](../app/pipeline/constants/schemas_constants.py) | `SchemasConstants` | `_WHEN_RE`, `_YEAR_RE`, `_SCREEN_NUMBER_RE`, `KEYWORD_MAX_WORDS`, `HOOK_MAX_WORDS`, `MEDIA_SHOT_KINDS`, `REELS_SHOT_KINDS`, `_STEP_NAMES`, `_OBJECTIVE_FIELDS`, `PUBLIC_DOMAIN_LICENSES`, `ATTRIBUTION_LICENSES`, `CITATION_LICENSE`, `AUDIO_LIBRARY_LICENSE`, `MAX_MUSIC_GAIN_DB`, `WINDOW_DAYS`, `READING_NUMBERS`, `APPROVED_STATES`, `STOCK_LICENSES`, `NUMBER_SEPARATORS`, `OVERLAY_SHOT_KINDS`, `HOST_CORNERS`, `MAX_CITATION_FRAMES`, `MAX_CITATION_MS`, `MUSIC_GAIN_DB`, `MUSIC_DIR`, `MUSIC_CATALOG_FILE`, `MUSIC_PLAN_FILE`, `METRICS_FILE`, `_EXCERPT_RE`, `PORTRAIT_SHOT_KINDS`, `ACCEPTED_LICENSES`, `GRAPHIC_SHOT_KINDS`, `_NOT_A_RECORD` |
| [`app/pipeline/constants/sfx_constants.py`](../app/pipeline/constants/sfx_constants.py) | `SfxConstants` | `MAX_GAIN_DB`, `COVERS_SPEECH`, `SFX_DIR`, `KIT_DIR`, `KIT_INDEX`, `SFX_PLAN_FILE`, `KIT_VOICE_REFERENCE_LUFS`, `MAX_CUES_PER_10S` |
| [`app/pipeline/constants/shots_constants.py`](../app/pipeline/constants/shots_constants.py) | `ShotsConstants` | `MIN_SHOT_MS`, `TARGET_AVERAGE_MS` |
| [`app/pipeline/constants/state_constants.py`](../app/pipeline/constants/state_constants.py) | `StateConstants` | `MANIFEST`, `TRANSITIONS` |
| [`app/pipeline/constants/text_fit_constants.py`](../app/pipeline/constants/text_fit_constants.py) | `TextFitConstants` | `NUMBER_OVER_MEDIA`, `NUMBER_FULL`, `COMPARE_LABEL`, `TIMELINE_LABEL`, `LOWER_THIRD_NAME`, `LOWER_THIRD_ROLE`, `NODE_LABEL_PER_LINE`, `NODE_ROLE_PER_LINE`, `NODE_LINES`, `EDGE_LABEL_CHARS`, `EDGE_VALUE_CHARS`, `READING_CHARS_PER_SECOND` |
| [`app/pipeline/constants/translation_constants.py`](../app/pipeline/constants/translation_constants.py) | `TranslationConstants` | `NARRATION_FILE`, `LINK_FILE`, `CONTENT_FILE`, `_PT_VALUES`, `_PT_SCALES`, `_EN_VALUES`, `_EN_SCALES`, `_EN_HUNDRED`, `_WORD`, `_LEXICONS` |
| [`app/pipeline/constants/usage_constants.py`](../app/pipeline/constants/usage_constants.py) | `UsageConstants` | `TOKEN_FIELDS` |
| [`app/providers/alignment/constants/groq_constants.py`](../app/providers/alignment/constants/groq_constants.py) | `GroqConstants` | `URL`, `PROMPT_CHARS` |
| [`app/providers/archives/constants/pexels_constants.py`](../app/providers/archives/constants/pexels_constants.py) | `PexelsConstants` | `API`, `PER_PAGE`, `LICENSE_URL`, `LICENSE_ID`, `PROVIDER` |
| [`app/providers/archives/constants/pixabay_constants.py`](../app/providers/archives/constants/pixabay_constants.py) | `PixabayConstants` | `API`, `PER_PAGE`, `MAX_QUERY_CHARS`, `LICENSE_URL`, `LICENSE_ID`, `PROVIDER` |
| [`app/providers/archives/constants/stock_constants.py`](../app/providers/archives/constants/stock_constants.py) | `StockConstants` | `IMAGE_SUFFIXES` |
| [`app/providers/archives/constants/unsplash_constants.py`](../app/providers/archives/constants/unsplash_constants.py) | `UnsplashConstants` | `API`, `PER_PAGE`, `LICENSE_URL`, `LICENSE_ID`, `PROVIDER` |
| [`app/providers/constants/errors_constants.py`](../app/providers/constants/errors_constants.py) | `ErrorsConstants` | `PROVIDER_ERROR_REASON`, `QUOTA_EXHAUSTED_REASON`, `MODEL_UNAVAILABLE_REASON`, `LICENSE_UNKNOWN_REASON`, `INVALID_OUTPUT_REASON`, `PAID_API_BLOCKED_REASON` |
| [`app/providers/constants/http_constants.py`](../app/providers/constants/http_constants.py) | `HttpConstants` | `CHUNK_BYTES`, `USER_AGENT` |
| [`app/providers/text/constants/ollama_constants.py`](../app/providers/text/constants/ollama_constants.py) | `OllamaConstants` | `NS_PER_MS` |
| [`app/providers/tts/constants/chatterbox_constants.py`](../app/providers/tts/constants/chatterbox_constants.py) | `ChatterboxConstants` | `WORKER`, `MODAL_CLIENT`, `MODEL_PREFIX`, `MAX_PART_CHARS`, `SENTENCE_GAP_MS`, `_SENTENCE_END`, `_CLAUSE_END`, `DEFAULT_DELIVERY` |
| [`app/providers/tts/constants/chatterbox_modal_client_constants.py`](../app/providers/tts/constants/chatterbox_modal_client_constants.py) | `ChatterboxModalClientConstants` | `FORWARDED` |
| [`app/providers/tts/constants/gemini_constants.py`](../app/providers/tts/constants/gemini_constants.py) | `GeminiConstants` | `API`, `TIMEOUT_S`, `SECONDS_PER_CHAR`, `SCENE_BREAK`, `TRANSIENT`, `MARGIN_S` |
| [`app/providers/tts/constants/kokoro_constants.py`](../app/providers/tts/constants/kokoro_constants.py) | `KokoroConstants` | `REPO_ID`, `SAMPLE_RATE`, `LANG_CODES` |
| [`app/render/constants/base_constants.py`](../app/render/constants/base_constants.py) | `BaseConstants` | `PREVIEW_HEIGHT` |
| [`app/render/constants/ffmpeg_constants.py`](../app/render/constants/ffmpeg_constants.py) | `FfmpegConstants` | `ENGINE_VERSION`, `FIT_MIN_ASPECT`, `SRT_TIME`, `CONCAT`, `AUDIO_VERSION`, `DUCKING`, `LIMITER` |
| [`app/render/constants/remotion_constants.py`](../app/render/constants/remotion_constants.py) | `RemotionConstants` | `PROJECT`, `TEMPLATE_GLOBS`, `MEDIA_KINDS` |
| [`app/settings/constants/settings_constants.py`](../app/settings/constants/settings_constants.py) | `SettingsConstants` | `CONFIG_FILE`, `ENV_OVERRIDES`, `SECRET_VARS` |
| [`app/storage/constants/json_files_constants.py`](../app/storage/constants/json_files_constants.py) | `JsonFilesConstants` | `REVIEW_FILE` |
| [`app/storage/constants/usage_sqlite_constants.py`](../app/storage/constants/usage_sqlite_constants.py) | `UsageSqliteConstants` | `SCHEMA` |

Permanecem nos próprios módulos: aliases de tipos, TypeVar, metadados Python (`__all__`),
campos/defaults de modelos, membros de enums e variáveis locais dependentes da execução.
As classes de serviço referenciam a constante quando precisam expor um atributo da interface.

Os únicos registros mutáveis globais permitidos pela guarda são `app.cli.HANDLERS` (handlers de execução)
e `app.bootstrap.DEFAULT_REGISTRY` (composição tipada de fábricas). São estado de composição,
não coleções anunciadas como constantes. A lista é explícita no teste e não constitui baseline de dívida.

Verificação da migração: 288 valores globais comparados antes/depois sem diferenças, 133 schemas
Pydantic preservados e testes de montagem/cache incluídos na suíte. Os demais valores são os sete do
grupo FFmpeg já extraído, um nome do armazenamento e quinze metadados de provedores e erros.
