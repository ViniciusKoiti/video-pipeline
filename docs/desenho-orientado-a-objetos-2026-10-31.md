# Como fica o `app/` depois da orientação a objetos (desenho-alvo, 2026-10-31)

Estado-alvo, não implementação: nenhum arquivo deste desenho existe ainda. Diz como o código fica quando os
scripts de `scripts/provisorio/` tiverem virado objetos e comandos `vp`, com as interfaces de cada objeto, a
árvore de arquivos, o caminho de um episódio pelos objetos e os testes. Vem de
`docs/analise-scripts-provisorios-2026-10-31.md` (o inventário e o §5) e respeita o gate de tamanho de
`docs/analise-tamanho-modulos-2026-10-31.md` (até 200 linhas de código por arquivo e 50 por função, decisão do
dono em 2026-10-31: objetos primeiro, aperto das linhas depois).

**Antes de implementar:** usar o [fluxo e seus gates](fluxo-refatoracao-solid-2026-11-01.md) para resolver
os contratos apontados na [análise SOLID](analise-gaps-solid-2026-10-31.md). As assinaturas abaixo continuam
sendo esboços; em especial, `Production.run()`, o escopo de `EpisodeFolder` e a identidade TTS exigem os
critérios RF1–RF4 antes de orientar a migração.

Os esboços abaixo são interfaces (assinaturas e docstrings), não corpos. Tipos citados que já existem:
`ManifestStore`, `Context`, `TTSProvider`, `ArchiveProvider`, `RenderEngine`, `SpeechRequest`, `RenderResult`,
`SceneOutcome`, `Clock`, `Glossary`, os manifestos de `schemas.py` e os modelos de `sfx.py`.

## 1. As regras do desenho

1. **Porta** é `Protocol`; **adapter** é uma classe por provedor; **valor** é `dataclass(frozen=True)`, ou modelo
   pydantic quando vai para arquivo; **serviço** é classe com estado entre passos e portas no construtor;
   **transformação pura** é função. Classe só onde há estado ou recurso (pasta, cache, processo, provedor).
2. Quem monta objetos é `app/commands/*`, a partir do `Context`. Nenhum objeto lê `sys.argv`, `os.environ` ou
   `Settings`: o que ele precisa entra por valor no construtor.
3. `EpisodeFolder` é o único que sabe nomes de arquivo e pastas de um episódio.
4. Falha de provedor é `SceneOutcome` na cena (`app/pipeline/failures.py`), nunca `SystemExit`: a cena para, o
   episódio segue (§2.1).
5. Arquivo de etapa aprovada não é sobrescrito: toda escrita de manifesto passa por `write_output` (§2.6).
6. Rede só com pedido do dono na sessão (§14): o comando imprime `info.name` e `info.remote` do provedor antes
   de chamar; o objeto não sabe que é remoto.
7. `app/pipeline/*` importa só portas, valores e `app/media/*` (`tests/test_architecture.py`); os adapters
   implementam os métodos novos; `bootstrap.py` continua sendo a única raiz de composição.
8. Cada módulo novo cabe em 200 linhas de código e cada função em 50 (`tests/test_tamanho_modulos.py`).

## 2. A árvore de arquivos depois

```
app/
  cli.py                          muda   Command ganha `module`; build_parser e main tratam todos iguais
  commands/
    postiz.py, postiz_cadeia.py   igual
    usage.py                      igual
    sources.py                    novo   vp sources add | declare
    brief.py                      novo   vp brief radar | formato
    assets.py                     novo   vp assets buscar | baixar
    music.py                      novo   vp music add | use | list
    producao.py                   novo   vp voice | subs | render (handlers finos sobre Production)
    short.py                      novo   vp short voz | tempos | sfx | juntar | boca | gate
    audio.py                      novo   vp audio
    evolucao.py                   novo   vp evolucao gerar | guardar | comparar | lado-a-lado
    metricas.py                   novo   vp metricas iniciar | ler | pendentes | tabela
    export.py                     novo   vp export (primeira fatia: livros e créditos)
  pipeline/
    episode.py                    novo   EpisodeFolder
    voice.py                      novo   SpeechLine, VoiceKey, Naming, VoiceLibrary, Narrator
    production.py                 novo   ProductionOptions, ProductionReport, Production, assemble_episode()
    short.py                      novo   Narration, NarrationLine (vêm de translation.py), VoicedLine,
                                         VoicedNarration, MotionContent, FitRow, ShortProduction
    sources.py                    novo   SourceDraft, Extracted, SourceRegistry, fetch_url(), from_file(), declared()
    assets.py                     novo   CandidateRequest, CandidateBatch, CandidateRecord, SearchFailure,
                                         CandidateSet, CandidateSearch, CandidateIndex, AssetIntake
    briefs.py                     novo   Placement, EpisodeBrief[T], radar_brief(), format_brief()
    music.py                      muda   + TrackDraft, MusicLibrary
    ports.py                      muda   Context + tts_final, tts_named(), word_aligner, archive_cascade()
    translation.py                muda   Narration e NarrationLine saem para short.py; importa de lá
    failures.py                   igual  SceneOutcome passa a ser usado pelo Narrator
  media/
    mix.py                        novo   SpeechSpan, MixResult, AudioMix, speech_bounds()
    earshot.py                    muda   + Earshot, AudioReviewPlan
    evolution.py                  muda   + TemplateSnapshot
  providers/
    tts/base.py                   muda   + TTSProvider.fingerprint(), BatchTTS, Closeable
    tts/kokoro.py, gemini.py, chatterbox.py   mudam   implementam fingerprint(); gemini declara BatchTTS
    archives/base.py              muda   + ArchiveCascade
  bootstrap.py                    muda   LazyContext.archive_cascade()
scripts/
  bench/                          checagem_local.py, teste_voz_gemini.py
  ferramentas/                    sprites_apresentador.py, clipe_tempos.py, clipe_reconhecer.py
  provisorio/                     deixa de existir
tests/
  fakes/__init__.py               muda   FakeTTS.fingerprint(), FakeBatchTTS, FakeContext completo
  test_voice.py, test_production.py, test_short.py, test_mix.py, test_sources.py, test_assets.py,
  test_briefs.py, test_music_library.py                               novos
  test_shorts_tec.py, test_metrics.py (parte), test_chatterbox_tts.py (parte), test_narration.py (parte)
                                  migram: importam de app/ em vez de carregar o script por caminho
```

## 3. Os objetos, um a um

### 3.1 `EpisodeFolder` (`app/pipeline/episode.py`)

```python
@dataclass(frozen=True)
class EpisodeFolder:
    """A pasta de um episódio: o único lugar que sabe os nomes dos arquivos (CLAUDE.md §3, mapa)."""

    store: ManifestStore
    episode_id: str

    @property
    def root(self) -> Path: ...
    def scenes(self) -> ScenesManifest: ...
    def sources(self) -> SourcesManifest | None: ...        # None quando não há sources.json
    def music_plan(self) -> MusicPlan | None: ...
    def glossary(self) -> Glossary: ...                     # voice/glossary.json, vazio se não existe
    @property
    def voice_dir(self) -> Path: ...
    @property
    def renders(self) -> Path: ...
    @property
    def candidates(self) -> Path: ...
    def media(self, asset_id: str) -> str: ...              # "assets/<id>.<ext>" ou LookupError
    def track(self, asset_id: str) -> str: ...              # faixa de música, idem
    def write(self, name: str, manifest: BaseModel) -> None: ...   # write_output: recusa etapa aprovada
    def stage_final(self, video: Path, post_text: str) -> Path: ...  # renders/final.mp4 + legenda-post.txt
    def lock(self) -> AbstractContextManager[None]: ...     # store.lock
```

Substitui os `settings.data_dir / "episodes" / id / ...` dos scripts. As funções de `app/media/` que hoje recebem
`episode_dir: Path` continuam recebendo `Path`: o `EpisodeFolder` entrega `folder.root`. As 20 constantes de
nome de arquivo migram para cá aos poucos (questão 6 do §8 da análise dos scripts).

### 3.2 Voz: `SpeechLine`, `VoiceKey`, `VoiceLibrary`, `Narrator` (`app/pipeline/voice.py`)

```python
@dataclass(frozen=True)
class SpeechLine:
    """Uma fala a gerar: a cena do longo ou a linha da narração do Short."""

    id: str                 # "S01", ou "fora-3" para fala sem cena no JSON do motion-video
    text: str               # o texto do roteiro, com <short pause>
    delivery: str = "neutral"


class Naming(StrEnum):
    LONG = "long"           # <cena>-<provedor>-<digest>.wav (o de hoje no longo)
    SHORT = "short"         # <cena>-<provedor>-<idioma>-<digest>.wav (o de hoje no Short)


@dataclass(frozen=True)
class VoiceKey:
    """O que decide o nome do WAV: tudo o que, se mudar, pede fala nova."""

    line_id: str
    provider: str
    language: str
    fingerprint: str        # TTSProvider.fingerprint(text, language, delivery): o adapter responde por si
    spoken: str             # o texto que a voz lê (glossário aplicado)

    @property
    def digest(self) -> str: ...                            # sha256(f"{fingerprint}|{spoken}")[:10]
    def stem(self, naming: Naming) -> str: ...              # a parte do nome antes do digest
    def file_name(self, naming: Naming) -> str: ...


class VoiceLibrary:
    """A pasta `voice/`: só arquivos, nenhum provedor."""

    def __init__(self, folder: Path, naming: Naming) -> None: ...
    def path(self, key: VoiceKey) -> Path: ...
    def has(self, key: VoiceKey) -> bool: ...
    def stale(self, key: VoiceKey) -> list[Path]: ...       # mesmo stem, outro digest
    def promote(self, tmp: Path, key: VoiceKey) -> Path: ...  # só depois de o WAV medir no ffprobe (#188)
    def prune(self, keep: Iterable[Path]) -> list[Path]: ...   # apaga o obsoleto, nunca antes de gerar o novo


class Narrator:
    """Gera as falas que faltam com um TTSProvider; em lote quando o provedor oferece; falha fica na cena."""

    def __init__(
        self, tts: TTSProvider, provider_name: str, language: str, library: VoiceLibrary, glossary: Glossary
    ) -> None: ...
    def key(self, line: SpeechLine) -> VoiceKey: ...
    def plan(self, lines: Sequence[SpeechLine]) -> list[SpeechRequest]: ...   # só as sem WAV
    def synthesize(self, requests: Sequence[SpeechRequest]) -> list[SceneOutcome[Path]]: ...
    def __enter__(self) -> Narrator: ...
    def __exit__(self, *exc: object) -> None: ...           # close() se o provedor é Closeable
```

`synthesize` agrupa só quando `isinstance(tts, BatchTTS)` (grupos até `max_batch_chars`; cena com pausa vai
sozinha, ADR 015), gera cena a cena quando o lote é recusado (`InvalidOutput`) e transforma `ProviderError` em
`SceneOutcome(needs_review)` daquela cena. Substitui `voice_fingerprint`, `long_speech_tag`, `batches`,
`generate` e o laço de `glob`/`unlink` do `montar_episodio.py`, e `wav_name` e `cmd_voz` do `shorts_tec.py`.

A chave de hoje continua válida: com `fingerprint()` devolvendo a mesma string que os scripts montam
(`chatterbox_modal|v3|pt|<hash>|pausa400|entrega:hook|frases300`), nenhum WAV em cache é regenerado. A única
mudança de chave é a do #190: a entrega não neutra do Chatterbox passa a levar `exaggeration` e `cfg_weight`,
e as cenas com entrega são geradas uma vez de novo.

### 3.3 As portas de voz (`app/providers/tts/base.py`)

```python
class TTSProvider(Protocol):
    info: ProviderInfo

    def synthesize_speech(self, request: SpeechRequest) -> SpeechResult: ...
    def fingerprint(self, text: str, language: str, delivery: str = "neutral") -> str:
        """O que muda a fala além do texto: modelo, voz, referência, pausa, entrega. Só quem sabe é o adapter."""


@runtime_checkable
class BatchTTS(Protocol):
    max_batch_chars: int

    def synthesize_many(self, requests: Sequence[SpeechRequest]) -> list[SpeechResult]: ...


@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...
```

| Adapter | `fingerprint` devolve | Declara |
|---|---|---|
| `KokoroTTS` | `kokoro\|<voz>` mais `\|pausa<ms>` quando o texto tem pausa | — |
| `GeminiTTS` | `gemini\|<modelo>\|<voz>\|<estilo>` | `BatchTTS` (`max_batch_chars = 1200`) |
| `ChatterboxTTS` (local e Modal) | `<nome>\|<modelo>\|<idioma>\|<hash da referência>` mais `\|pausa<ms>`, `\|entrega:<nome>=<exaggeration>,<cfg_weight>` quando não neutra e `\|frases<N>` quando alguma frase passa de `MAX_PART_CHARS` | `Closeable` |
| `FakeTTS` (testes) | `fake` | `FakeBatchTTS` nos testes de lote |

Tira do orquestrador `CLONED`, `BATCH_CHARS`, `voice_fingerprint`, `long_speech_tag`, o `getattr(tts,
"synthesize_many")` e o `getattr(tts, "close")`; `reference_hash` e `MAX_PART_CHARS` ficam onde estão, dentro
do adapter.

### 3.4 `Production` (`app/pipeline/production.py`)

```python
@dataclass(frozen=True)
class ProductionOptions:
    final: bool = False          # voz do vídeo final (tts_final) em vez da dos rascunhos (tts)
    voice: str | None = None     # --voz=<nome>: uma voz registrada pelo nome (tts_named)
    preview: bool = False        # 720p
    render: bool = True
    word_captions: bool = False  # Whisper da Groq: remoto, só com pedido do dono


@dataclass(frozen=True)
class ProductionReport:
    provider: str
    voice: list[SceneOutcome[Path]]      # uma entrada por cena
    episode: EpisodeManifest | None      # None se alguma cena ficou sem voz
    captions: str                        # o que o sync_captions fez ("mantida", "gerada", ...)
    pacing: list[str]                    # pacing_warnings
    render: RenderResult | None
    lufs: float | None                   # só com trilha


class Production:
    """Voz, legenda, episode.json e render de um episódio, cada etapa por run_step (lock, estado, reuso)."""

    def __init__(self, context: Context, folder: EpisodeFolder, options: ProductionOptions, now: Clock) -> None: ...
    def preconditions(self) -> list[str]: ...        # vazio = pode seguir (regra do gate: questão 3)
    def voice(self) -> list[SceneOutcome[Path]]: ...  # run_step(Step.VOICE): Narrator + VoiceLibrary(LONG)
    def episode(self) -> EpisodeManifest: ...         # assemble_episode + trilha; folder.write("episode.json")
    def captions(self) -> str: ...                    # run_step(Step.SUBS): por frase e, se pedido, por palavra
    def render(self) -> RenderResult: ...             # context.renderer(episode.format); Step.PREVIEW
    def run(self) -> ProductionReport: ...            # voice → episode → captions → render, parando no 1º erro


def assemble_episode(
    scenes: ScenesManifest,
    wavs: Mapping[str, Path],
    duration_ms: Callable[[Path], int],
    media: Callable[[str], str],
    sources: SourcesManifest | None,
    music: Sequence[EpisodeMusic] = (),
) -> EpisodeManifest:
    """Cenas em sequência com a duração real de cada WAV, os planos no tempo (shots.py), rodapé e trilha."""
```

O provedor vem do `Context`: `tts_named(options.voice)` se houver nome, senão `tts_final` com `final=True`,
senão `tts`. O `run_step` já trava o episódio por etapa; `run()` não trava por fora (#193). `render` usa o estado
`Step.PREVIEW`, que é o que o gate 4 avalia; se o dono quiser separar prévia de final no `manifest.json`, entra um
`Step.RENDER` (ponto a decidir). `assemble_episode` é função porque não tem estado: recebe a duração injetada
(`duration_ms`) e é testada sem ffprobe.

### 3.5 Short: `Narration`, `VoicedNarration`, `MotionContent`, `ShortProduction` (`app/pipeline/short.py`)

```python
class NarrationLine(Model):           # vem de translation.py, sem mudar
    scene: str | None = None
    text: str
    delivery: str | None = None


class Narration(Model):               # idem; ganha o método
    language: str
    lines: list[NarrationLine]

    def speech_lines(self) -> list[SpeechLine]: ...


class VoicedLine(Model):
    scene: str | None
    text: str
    delivery: str
    wav: str                           # "voice/<nome>.wav"
    seconds: float
    speech: tuple[float, float]        # onde a fala começa e termina dentro do WAV


class VoicedNarration(Model):         # <narracao>.voz.json: o que `voz` entrega a `tempos`, `juntar` e `boca`
    language: str
    provider: str
    lines: list[VoicedLine]

    def spans(self, folder: Path) -> dict[str, SpeechSpan]: ...


@dataclass(frozen=True)
class FitRow:
    scene_id: str
    before: float
    after: float


class MotionContent:
    """O JSON do motion-video, só o que o auto-play toca: fps, id, durationSec, type e host de cada cena."""

    def __init__(self, data: dict[str, Any]) -> None: ...
    @classmethod
    def load(cls, path: Path) -> MotionContent: ...
    def save(self, path: Path) -> None: ...
    @property
    def fps(self) -> int: ...
    @property
    def scene_ids(self) -> list[str]: ...
    def starts(self) -> dict[str, float]: ...                # a mesma conta do motion-video: frames inteiros
    def durations(self) -> dict[str, float]: ...
    def has_host(self) -> bool: ...
    def fitted(self, seconds: Mapping[str, float], pad: float = 0.3) -> tuple[MotionContent, list[FitRow]]:
        """Cada cena esticada até a fala caber; devolve um JSON novo, não altera o atual."""


class ShortProduction:
    """Os passos do Short por JSON (ADR 033): a voz, os tempos, os efeitos, a junção, a boca e a pasta de gate."""

    def __init__(
        self, context: Context, folder: Path, narration: Narration, voice: str | None, now: Clock
    ) -> None: ...
    def voice(self) -> VoicedNarration: ...                                   # Narrator + VoiceLibrary(SHORT)
    def fit(self, content: MotionContent) -> tuple[MotionContent, list[FitRow]]: ...
    def check_sfx(self, content: MotionContent, plan: SfxPlan) -> tuple[list[PlacedSfx], float | None]: ...
    def join(self, video: Path, content: MotionContent, out: Path, plan: SfxPlan | None) -> MixResult: ...
    def mouth(self, content: MotionContent, manifest: Path | None, text: Path | None) -> dict[str, Any]: ...
    def gate(self, video: Path, post: Mapping[str, Any], episode: EpisodeFolder) -> Path: ...
```

`ShortProduction` e `Production` não herdam uma da outra: compartilham `Narrator`, `VoiceLibrary` e as funções
de `app/media/`. `mouth` continua devolvendo o dicionário que a montagem em TSX lê (contrato do kit).

### 3.6 `AudioMix` (`app/media/mix.py`)

```python
@dataclass(frozen=True)
class SpeechSpan:
    wav: Path
    begin: float
    end: float

    @property
    def seconds(self) -> float: ...


@dataclass(frozen=True)
class MixResult:
    path: Path
    duration_s: float
    lufs: float
    problem: str | None                # loudness_problem


class AudioMix:
    """O filtro do ffmpeg que põe falas e efeitos sobre o vídeo, em estéreo e no alvo de −14 LUFS (ADR 035)."""

    def __init__(self, video: Path, target_lufs: float = TARGET_LUFS) -> None: ...
    def speech(self, span: SpeechSpan, at_ms: int) -> AudioMix: ...
    def effect(self, file: Path, at_ms: int, trim_s: float, gain_db: float) -> AudioMix: ...
    def keep_video_audio(self) -> AudioMix: ...
    def filter(self) -> str: ...                                   # a string do filter_complex (o teste de hoje)
    def command(self, out: Path) -> list[str]: ...
    def render(self, out: Path, run: Runner = subprocess.run) -> MixResult: ...


def speech_bounds(path: Path, run: Runner = subprocess.run) -> SpeechSpan:
    """Onde a fala começa e termina no WAV, pelo silencedetect; função porque não tem estado."""
```

Substitui `mix_filter`, `bounds_from_log`, `speech_bounds` e o corpo de `cmd_juntar`. `Runner` é um
`Callable` injetável para o teste não chamar o ffmpeg.

### 3.7 Fontes: `SourceDraft`, `Extracted`, `SourceRegistry` (`app/pipeline/sources.py`)

```python
@dataclass(frozen=True)
class SourceDraft:
    """O que o dono informa sobre a fonte, antes de ela ter id."""

    title: str
    kind: SourceKind
    url: str | None = None             # None na fonte declarada
    authors: tuple[str, ...] = ()
    interested: bool = False
    notes: str = ""


@dataclass(frozen=True)
class Extracted:
    raw: bytes
    suffix: str                        # "html" | "pdf" | "md" | "txt"
    paragraphs: tuple[str, ...]


def fetch_url(url: str, dest: Path, download: Downloader, pdf_text: PdfText) -> Extracted: ...
def from_file(path: Path, pdf_text: PdfText) -> Extracted: ...        # PDF salvo à mão (servidor que recusa o robô)
def declared(path: Path) -> Extracted: ...                            # cada linha não vazia é um trecho


class SourceRegistry:
    """Registra uma fonte no episódio: bruto, texto, trechos numerados e a linha no sources.json."""

    def __init__(self, folder: EpisodeFolder) -> None: ...
    def next_id(self) -> str: ...                                     # "source-NN" livre
    def register(self, draft: SourceDraft, extracted: Extracted, now: datetime) -> Source: ...
```

`Downloader` é a assinatura de `app.providers.http.download`; `PdfText` a de quem chama o `pdftotext`. As três
funções devolvem o mesmo valor, e o registro é um só: some a duplicação entre `baixar_fonte.py` e
`fonte_declarada.py`.

### 3.8 Ativos: candidatos e entrada (`app/pipeline/assets.py`)

```python
class CandidateRequest(Model):        # um item de pedidos.json
    id: str
    plano: str
    consultas: list[str]
    midias: list[Media] = ["video"]
    min_duration_s: float | None = None
    orientacao: Orientation | None = None   # None = a do scenes.json


class CandidateBatch(Model):
    pedidos: list[CandidateRequest]


class CandidateRecord(Model):
    banco: str
    consulta: str
    midia: Media
    largura: int | None
    altura: int | None
    duracao_s: float | None
    miniatura: str | None
    ativo: Asset


class SearchFailure(Model):
    banco: str
    consulta: str
    motivo: str


class CandidateSet(Model):            # candidatos/<pedido>.json
    pedido: CandidateRequest
    candidatos: list[CandidateRecord]
    falhas: list[SearchFailure]


class CandidateSearch:
    """Cada consulta em cada banco em cada mídia; falha de um banco fica registrada e não interrompe (§2.1)."""

    def __init__(self, archives: Sequence[ArchiveProvider], limit: int = 5) -> None: ...
    def run(self, request: CandidateRequest, orientation: Orientation) -> CandidateSet: ...


class CandidateIndex:
    """A pasta candidatos/ do episódio."""

    def __init__(self, folder: Path) -> None: ...
    def save(self, found: CandidateSet) -> Path: ...
    def by_asset_id(self) -> dict[str, CandidateRecord]: ...


class AssetIntake:
    """Baixa o candidato escolhido pelo adapter do banco dele e grava assets/<id>.json em needs_review."""

    def __init__(self, archives: Mapping[str, ArchiveProvider], folder: EpisodeFolder) -> None: ...
    def take(self, record: CandidateRecord, scene_id: str) -> Asset: ...
```

No `Context`, `archive_cascade()` devolve `ArchiveCascade(available, skipped)` (`app/providers/archives/base.py`),
com o motivo de cada banco pulado (sem adapter, sem chave); o `archives` de hoje continua para quem já o usa.
O comando imprime os pulados antes da busca (#192).

### 3.9 Música, briefs, earshot e evolução

```python
# app/pipeline/music.py
@dataclass(frozen=True)
class TrackDraft:
    title: str
    moods: tuple[str, ...]
    vocals: bool
    artist: str | None = None
    loops: bool = False
    bpm: int | None = None
    license_id: str = AUDIO_LIBRARY_LICENSE
    attribution: str = ""


class MusicLibrary:
    """data/music/: as faixas que o dono baixou, o ativo de cada uma e o catalog.json."""

    def __init__(self, music_dir: Path) -> None: ...
    def catalog(self) -> MusicCatalog: ...
    def add(self, file: Path, draft: TrackDraft, now: datetime, lufs: Lufs, duration_ms: Duration) -> MusicTrack: ...
    def copy_to(self, folder: EpisodeFolder, asset_id: str) -> list[Path]: ...


# app/pipeline/briefs.py
class Placement(StrEnum):
    UNCHANGED = "igual"
    PLACED = "colocado"
    REPLACED = "trocado"


class EpisodeBrief(Generic[T]):
    """Cópia datada de um perfil (radar ou formato) na pasta do episódio: não sobrescreve sem `replace`."""

    def __init__(self, folder: EpisodeFolder, file_name: str, model: type[T], kept_name: Callable[[T], str]) -> None: ...
    def current(self) -> T | None: ...
    def place(self, text: str, replace: bool = False) -> Placement: ...   # ValueError: já há outro e replace=False


def radar_brief(folder: EpisodeFolder) -> EpisodeBrief[RadarBrief]: ...
def format_brief(folder: EpisodeFolder) -> EpisodeBrief[FormatBrief]: ...


# app/media/earshot.py
class Earshot:
    """O earshot no ambiente dele (EARSHOT_PYTHON): a configuração vive aqui, não em cada chamada."""

    def __init__(self, python: Path, threads: int) -> None: ...
    def timeline(self, media: Path, cuts: Sequence[float], out: Path) -> Review: ...


@dataclass(frozen=True)
class AudioReviewPlan:
    cuts: tuple[float, ...]
    expected: frozenset[float]         # onde o ataque de cada efeito por deslocamento tem de cair

    @classmethod
    def from_episode(cls, episode: EpisodeManifest) -> AudioReviewPlan: ...
    @classmethod
    def from_content(cls, content: MotionContent, plan: SfxPlan | None, kit: SfxKit | None) -> AudioReviewPlan: ...


# app/media/evolution.py
@dataclass(frozen=True)
class TemplateSnapshot:
    commit: str
    template_hash: str
    motion_kit: str

    @classmethod
    def from_worktree(cls, root: Path, git: Git) -> TemplateSnapshot: ...
    @classmethod
    def from_ref(cls, root: Path, ref: str, git: Git) -> TemplateSnapshot: ...
```

Métricas não ganham objeto: `app/pipeline/metrics.py` já é valores e funções; só o comando entra.

### 3.10 O registro de comandos (`app/cli.py`)

```python
class CommandModule(Protocol):
    """Um comando com subcomandos próprios (postiz, usage, sources, short...)."""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None: ...
    def run(self, args: argparse.Namespace, context: Context) -> int: ...
    def report_error(self, message: str) -> int: ...


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    step: int
    takes_episode: bool = True
    add_arguments: Callable[[argparse.ArgumentParser], None] | None = None
    module: CommandModule | None = None
```

`build_parser` e `main` tratam todos iguais: `handler = command.module.run if command.module else
HANDLERS.get(name)`, e erro de configuração vai para `module.report_error`. Some o `if args.command not in
("postiz", "usage")`. Um handler fino de produção, para mostrar o tamanho:

```python
# app/commands/producao.py
def run_voice(args: argparse.Namespace, context: Context) -> int:
    folder = EpisodeFolder(context.store, args.episode_id)
    options = ProductionOptions(final=args.final, voice=args.voz, render=False)
    production = Production(context, folder, options, now=_now)
    if problems := production.preconditions():
        return _refuse("vp voice", problems)
    _announce(context, options)                     # imprime provedor e remote antes de chamar (§14)
    report = production.run()
    _print_scenes(report.voice)
    return 0 if all(o.status is Status.COMPLETED for o in report.voice) else 1
```

## 4. Um episódio de ponta a ponta nos objetos

Longo (ensaio), na ordem do §15 do CLAUDE.md:

1. `vp sources add <id> <url> --title ...` → `fetch_url` → `SourceRegistry.register` → `sources.json`,
   `sources/raw/`, `sources/`, `excerpts/`. Gate 1 como hoje.
2. Agentes escrevem `facts.json`, `outline.md`, `scenes.json`; `vp check` e `vp checagem` como hoje.
3. `vp voice <id>` → `Production.voice` (Kokoro: `Narrator` + `VoiceLibrary(LONG)`) → `Production.episode`
   (`assemble_episode`, `folder.write("episode.json")`) → `Production.captions`. `vp render <id> --preview` →
   `context.renderer(EXPLAINER)`. Gate 2 na prévia.
4. `vp assets buscar <id> pedidos.json` → `CandidateSearch.run` por pedido → `CandidateIndex.save`. O dono
   escolhe; `vp assets baixar <id> <cena> <ids>` → `AssetIntake.take`. Gate 3 por ativo.
5. `vp music use <id> <faixa>` → `MusicLibrary.copy_to`; `diretor-musical` escreve `music.json`.
6. `vp voice <id> --final` (Modal) → `Production` com `tts_final`; `vp render <id>` → final com trilha e
   loudness. Gate 4; depois `vp postiz` como hoje.

Short técnico (ADR 033, 035, 036):

1. `vp short voz <pasta> narracao.pt.json` → `ShortProduction.voice` → `narracao.pt.voz.json`
   (`VoicedNarration`).
2. `vp short tempos` → `MotionContent.load` → `fitted` → `content.pt.voz.json`; render do kit fora do `vp`.
3. `vp short sfx` → `ShortProduction.check_sfx` (`sfx.py` como hoje).
4. `vp short juntar ... --sfx` → `AudioMix` → `MixResult` com loudness.
5. `vp audio <mp4> --content ... --sfx ...` → `AudioReviewPlan.from_content` → `Earshot.timeline` →
   `review_problems`.
6. `vp short gate <mp4> post.json --episodio=<id>-pt` → `EpisodeFolder.stage_final`. Gate 4 e `vp postiz`.

## 5. O que fica como está

`schemas.py`, `check.py`, `gates.py`, `state.py`, `shots.py`, `captions.py`, `word_captions.py`, `sfx.py`,
`loudness.py`, `probe.py`, `pronunciation.py`, `narration.py`, `pauses.py`, `envelope.py`, `host.py`,
`metrics.py`, `affiliate.py`, `numbers.py`, `molde.py`, `radar.py` (só perde a cópia datada para `briefs.py`),
os motores de render, o armazenamento e o Postiz. Os adapters de voz ganham um método. A partição desses
arquivos pelo gate de 200 linhas é a etapa seguinte, não esta.

## 6. Correspondência script → objeto

| Hoje | Depois |
|---|---|
| `montar_episodio.voice_fingerprint`, `long_speech_tag`, `CLONED`, `BATCH_CHARS` | `TTSProvider.fingerprint`, `BatchTTS` |
| `montar_episodio.batches`, `generate` | `Narrator.synthesize` |
| `montar_episodio.main` (laço dos WAVs) | `Narrator.plan` + `VoiceLibrary` |
| `montar_episodio.main` (laço do `cursor`), `media_path`, `music` | `assemble_episode`, `EpisodeFolder.media`, `EpisodeFolder.track` |
| `montar_episodio.captions`, `word_captions` | `Production.captions` |
| `montar_episodio.main` (render, loudness) | `Production.render` |
| `shorts_tec.Line`, `load_lines` | `NarrationLine`, `Narration.speech_lines` |
| `shorts_tec.wav_name` | `VoiceKey.file_name(Naming.SHORT)` |
| `shorts_tec.bounds_from_log`, `speech_bounds`, `Speech` | `speech_bounds`, `SpeechSpan` |
| `shorts_tec.scene_starts`, `fit_durations` | `MotionContent.starts`, `MotionContent.fitted` |
| `shorts_tec.mix_filter`, `cmd_juntar` | `AudioMix` |
| `shorts_tec.cmd_voz`, `cmd_tempos`, `cmd_sfx`, `cmd_boca`, `cmd_gate`, `voiced` | `ShortProduction.*`, `VoicedNarration` |
| `baixar_fonte.main`, `fonte_declarada.main`, `line_paragraphs` | `fetch_url`, `from_file`, `declared`, `SourceRegistry` |
| `buscar_candidatos.available_archives`, `main`, `_record` | `Context.archive_cascade`, `CandidateSearch`, `CandidateRecord` |
| `baixar_escolhidos.main` | `CandidateIndex.by_asset_id`, `AssetIntake.take` |
| `catalogo_musica.add`, `use`, `list_tracks` | `MusicLibrary.add`, `copy_to`, `catalog` |
| `radar_resumo.main`, `formato_resumo.main` | `EpisodeBrief.place` |
| `conferir_audio.cuts_from_*`, `expected_from_sfx`, `main` | `AudioReviewPlan`, `Earshot.timeline` |
| `evolucao.template_info`, `project_info`; `gerar` por subprocesso | `TemplateSnapshot`; `Production(preview=True, voice="gemini")` |
| `metricas.main` | `app/commands/metricas.py` |
| `livros_afiliado.main` | `app/commands/export.py` |

## 7. Os testes

| Teste | O que prova | Com o quê |
|---|---|---|
| `test_voice.py` | `VoiceKey.digest` igual ao nome de hoje para o mesmo fingerprint e texto; `stale` acha só o mesmo stem; `promote` não deixa WAV pela metade; `Narrator.plan` só pede o que falta; lote só com `BatchTTS`; `ProviderError` vira `SceneOutcome(needs_review)` daquela cena e as outras seguem; `close()` chamado | `FakeTTS`, `FakeBatchTTS`, `tmp_path` |
| `test_production.py` | `run()` passa por `run_step` (estado em `manifest.json`), reutiliza com o mesmo hash, usa o renderer configurado, escreve `episode.json` pelo store e recusa quando `preconditions()` acusa | `FakeContext` com `InMemoryStore`, `FakeTTS`, `FakeRender` |
| `test_short.py` (migra `test_shorts_tec.py`) | `MotionContent.starts` e `fitted` com os casos de hoje; `VoicedNarration` lê o que escreve | JSON em memória |
| `test_mix.py` (migra o `mix_filter` de `test_sfx.py`) | `AudioMix.filter` igual à string de hoje; `speech_bounds` sobre um log gravado | `Runner` falso |
| `test_sources.py` | `declared` faz um trecho por linha; `register` dá o próximo id, escreve os quatro arquivos e recusa `sources.json` aprovado | `InMemoryStore` |
| `test_assets.py` | `CandidateSearch.run` registra falha de um banco e segue; `AssetIntake.take` grava `sha256` e `needs_review` | `FakeArchive` |
| `test_briefs.py` | `place` igual, colocado, trocado e a recusa sem `replace` | `tmp_path` |
| `test_chatterbox_tts.py`, `test_narration.py`, `test_metrics.py` | passam a importar de `app/`; o que testavam no script testa o objeto | — |

Nenhum teste chama rede, ffmpeg, Kokoro ou Modal (§2.10); os que precisam de áudio real continuam `slow`.

## 8. O que o desenho ainda deixa ao dono

As questões do §8 de `docs/analise-scripts-provisorios-2026-10-31.md` que mudam este desenho: nomes dos comandos
(1), três comandos de produção ou um (2), pré-condições de `--final` e do render final (3), o nome do WAV do
longo com idioma (7) e a ADR das portas novas (9). O estado do render no `manifest.json` (`Step.PREVIEW` ou um
`Step.RENDER` novo) é o único ponto novo que este documento acrescenta.
