"""Voz e render de um episódio a partir do scenes.json (provisório até `vp voice` #16 e `vp render` #13).

Uso: `.venv/bin/python scripts/provisorio/montar_episodio.py <episode-id> [--no-render] [--preview]
     [--voz-final] [--voz=<nome>]`

- Narração por cena, em `voice/<cena>-<provedor>-<hash>.wav`: a voz dos rascunhos (`tts`, Kokoro) ou, com
  `--voz-final`, a do vídeo final (`tts_final`: a voz clonada do dono, ADR 016).
  O hash cobre o texto falado, o modelo, a voz
  e a direção de fala: a fala só é gerada de novo quando um deles muda, e uma voz não apaga as falas da outra.
- `--voz=<nome>` usa uma voz registrada pelo nome, fora da escolha do `providers.toml`: `gemini` (Charon,
  ADR 012; é a do vídeo-régua), `chatterbox`, `chatterbox_modal` (a mesma voz numa GPU do Modal, ADR 024) ou
  `kokoro`.
- A voz clonada gera uma cena por vez, dezenas de vezes mais devagar que o tempo real. O Gemini gera as cenas
  que faltam em lotes (várias cenas por chamada, cortadas nas pausas); lote que não
  pode ser cortado com segurança é gerado cena a cena. Cota esgotada: o script para, as falas já geradas ficam
  no cache e a próxima execução continua.
- Glossário de pronúncia (`voice/glossary.json`, opcional): a voz lê "FBI" como "efe bê i"; tela, legenda e
  âncoras mantêm a grafia do roteiro, e só as cenas com um termo do glossário ganham fala nova.
- Duração real de cada WAV (ffprobe) → tempo dos planos (app/pipeline/shots.py) → episode.json v2.
- Render pelo motor do formato explicativo (Remotion), com cache por cena.
- A mídia de cada plano de foto ou B-roll é `assets/<asset_id>.<ext>` (jpg, png, webp, mp4, webm).
- Com `sources.json` na pasta, cada plano com claims ganha a fonte do rodapé (ADR 011).
- Legenda por frase em `captions.srt` (#17, ADR 021), com o tempo tirado dos WAVs; o arquivo é editável e só
  é refeito quando a fala muda. Um SRT com intervalo inválido ou além do áudio para o script antes do render.
- `--legenda-palavra`: legenda palavra a palavra (ADR 023). Manda o WAV de cada cena ainda não reconhecida ao
  Whisper da Groq (remoto, camada gratuita: só com pedido do dono na sessão) e guarda o resultado em
  `captions.words.json`. Sem a opção, o arquivo que já existe é reaproveitado; cena sem ele fica na legenda
  por frase.
- Trilha (ADR 030): com `music.json` na pasta, cada entrada vira um trecho de `music` no `episode.json`, com o
  tempo tirado dos WAVs; a faixa é `assets/<asset_id>.<ext>` (mp3, m4a, wav, ogg), copiada do catálogo por
  `scripts/provisorio/catalogo_musica.py usar`. Depois do render, a loudness final é medida (alvo −14 LUFS).
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.bootstrap import LazyContext, build_context  # noqa: E402
from app.commands.errors import run  # noqa: E402
from app.media.captions import (  # noqa: E402
    SceneAudio,
    captions_key,
    episode_cues,
    parse_srt,
    review_hints,
    sync_captions,
    timing_problems,
)
from app.media.constants.captions_constants import CaptionsConstants  # noqa: E402
from app.media.constants.word_captions_constants import WordCaptionsConstants  # noqa: E402
from app.media.loudness import integrated_lufs, loudness_problem  # noqa: E402
from app.media.narration import strip_pauses  # noqa: E402
from app.media.pauses import silences  # noqa: E402
from app.media.probe import duration_ms  # noqa: E402
from app.media.pronunciation import load_glossary, respell  # noqa: E402
from app.media.word_captions import SceneSpeech, sync_words  # noqa: E402
from app.pipeline.assembly import EpisodeRenderer  # noqa: E402
from app.pipeline.constants.schemas_constants import SchemasConstants  # noqa: E402
from app.pipeline.models.naming import Naming  # noqa: E402
from app.pipeline.models.speech_line import SpeechLine  # noqa: E402
from app.pipeline.music import load_music_catalog, resolve_music  # noqa: E402
from app.pipeline.protection import ReviewWriteGuard  # noqa: E402
from app.pipeline.schemas import (  # noqa: E402
    EpisodeFormat,
    EpisodeManifest,
    EpisodeMusic,
    EpisodeScene,
    MusicPlan,
    ScenesManifest,
    SourcesManifest,
    VideoSpec,
)
from app.pipeline.shots import episode_shots, pacing_warnings  # noqa: E402
from app.pipeline.voice import Narrator, VoiceLibrary  # noqa: E402
from app.providers.errors import ProviderError  # noqa: E402
from app.providers.tts.base import TTSProvider, closing_tts  # noqa: E402
from app.settings import Settings  # noqa: E402

MEDIA_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm")
MUSIC_SUFFIXES = (".mp3", ".m4a", ".wav", ".ogg")


def generate_voice(tts: TTSProvider, scenes: ScenesManifest, episode_dir: Path) -> dict[str, Path]:
    """O WAV de cada cena (ADR 049): só as que faltam são geradas, em lote quando a voz oferece, e a antiga só
    sai depois da nova pronta e medida. Falta de fala é `VoiceIncomplete`; as prontas ficam para a próxima."""
    voice_dir = episode_dir / "voice"
    voice_dir.mkdir(exist_ok=True)
    glossary = load_glossary(episode_dir)
    narrator = Narrator(
        tts,
        scenes.language,
        VoiceLibrary(voice_dir, Naming.LONG),
        lambda wav: duration_ms(wav) / 1000,
        lambda text: respell(text, glossary),  # a grafia que a voz lê; sem termo, o texto do roteiro
    )
    lines = [SpeechLine(scene.id, scene.narration, scene.delivery or "neutral") for scene in scenes.scenes]
    with closing_tts(tts):  # a voz clonada mantém um processo com o modelo carregado
        return narrator.require(narrator.produce(lines))


def media_path(episode_dir: Path, asset_id: str) -> str:
    for suffix in MEDIA_SUFFIXES:
        if (episode_dir / "assets" / f"{asset_id}{suffix}").is_file():
            return f"assets/{asset_id}{suffix}"
    raise SystemExit(f"ativo {asset_id} sem arquivo de mídia em assets/")


def music(settings: Settings, episode_dir: Path, episode: EpisodeManifest) -> list[EpisodeMusic]:
    """Trechos da trilha (ADR 030) com o tempo dos WAVs; sem `music.json`, nenhum."""
    plan_path = episode_dir / SchemasConstants.MUSIC_PLAN_FILE
    if not plan_path.is_file():
        return []
    catalog = load_music_catalog(settings.data_dir)
    if catalog is None:
        raise SystemExit("music.json sem catálogo de faixas (data/music/catalog.json)")

    def track_file(asset_id: str) -> str:
        if not (episode_dir / "assets" / f"{asset_id}.json").is_file():
            raise SystemExit(f"faixa {asset_id} sem ativo no episódio (catalogo_musica.py usar)")
        for suffix in MUSIC_SUFFIXES:
            if (episode_dir / "assets" / f"{asset_id}{suffix}").is_file():
                return f"assets/{asset_id}{suffix}"
        raise SystemExit(f"faixa {asset_id} sem arquivo de áudio em assets/")

    plan = MusicPlan.model_validate_json(plan_path.read_text())
    return resolve_music(plan, episode, catalog, track_file)


def captions(
    episode_dir: Path,
    scenes: list[EpisodeScene],
    wavs: dict[str, Path],
    total_ms: int,
    before_change: Callable[[str], None] | None = None,
) -> None:
    """Gera ou mantém `captions.srt` e confere o arquivo que vai para o render (#17). `before_change` deixa o
    gate 4 aprovado recusar a troca antes de o arquivo ser tocado."""
    audio = [
        SceneAudio(
            start_ms=scene.start_ms, duration_ms=scene.duration_ms, narration=scene.narration,
            silences_ms=[(round(a * 1000), round(b * 1000)) for a, b in silences(wavs[scene.id])],
        )
        for scene in scenes
    ]
    cues, approximate = episode_cues(audio)
    key = captions_key([wavs[scene.id].name for scene in scenes])
    note = sync_captions(episode_dir, cues, key, before_change)
    found, problems = parse_srt((episode_dir / CaptionsConstants.CAPTIONS).read_text())
    problems += timing_problems(found, total_ms)
    if problems:
        raise SystemExit(f"{CaptionsConstants.CAPTIONS}: " + "; ".join(problems))
    print(f"legenda: {note}; {len(found)} blocos, {approximate} fronteira(s) no tempo proporcional")
    for n, hint in review_hints(found):
        print(f"  revisar bloco {n}: {hint}")


def word_captions(context: LazyContext, episode_dir: Path, scenes: list[EpisodeScene], language: str) -> None:
    """Palavras com tempo em `captions.words.json`; reconhece no Whisper remoto só com `--legenda-palavra`."""
    request = "--legenda-palavra" in sys.argv
    path = episode_dir / WordCaptionsConstants.WORDS
    if not request and not path.is_file():
        return
    speech = [SceneSpeech(s.id, s.audio, s.narration, s.duration_ms) for s in scenes]
    recognize = None
    if request:
        aligner = context.word_aligner
        recognize = lambda scene: aligner.recognize_words(  # noqa: E731
            episode_dir / scene.audio, language, prompt=strip_pauses(scene.narration)
        )
    name = f"{context.settings.providers.word_aligner}/{context.settings.groq_whisper.model}"
    try:
        report = sync_words(path, speech, recognize, name)
    except ProviderError as error:
        raise SystemExit(f"legenda palavra a palavra: {error.reason}: {error}. As cenas já reconhecidas "
                         f"ficam em {WordCaptionsConstants.WORDS}; rode de novo depois.") from error
    print(f"legenda palavra a palavra: {len(report.with_words)} cena(s), {report.unmatched} palavra(s) com "
          "tempo dividido entre as vizinhas")
    if report.without:
        print(f"  sem reconhecimento (ficam na legenda por frase): {', '.join(report.without)}; "
              "rode com --legenda-palavra")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    context = build_context(ROOT)
    settings = context.settings
    episode_dir = settings.data_dir / "episodes" / args[0]
    scenes = ScenesManifest.model_validate_json((episode_dir / "scenes.json").read_text())
    sources_path = episode_dir / "sources.json"  # fonte no rodapé dos planos (ADR 011)
    sources = None
    if sources_path.is_file():
        sources = SourcesManifest.model_validate_json(sources_path.read_text())
    final = "--voz-final" in sys.argv
    named = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--voz=")), None)
    tts = context.tts_named(named) if named else (context.tts_final if final else context.tts)
    started = time.monotonic()
    wavs = generate_voice(tts, scenes, episode_dir)

    episode_scenes, cursor = [], 0
    for scene in scenes.scenes:
        wav = wavs[scene.id]
        ms = duration_ms(wav)
        shots = episode_shots(
            scene, ms, lambda shot: media_path(episode_dir, shot.asset_id), sources, scenes.language
        )
        episode_scenes.append(
            EpisodeScene(
                id=scene.id, start_ms=cursor, duration_ms=ms, narration=scene.narration,
                audio=f"voice/{wav.name}", shots=shots, host_corner=scene.host_corner,
                delivery=scene.delivery,
            )
        )
        summary = ", ".join(f"{s.spec.kind} {s.duration_ms / 1000:.1f}" for s in shots)
        print(f"{scene.id}: {ms / 1000:5.2f} s | {summary}")
        cursor += ms
    print(f"voz: {time.monotonic() - started:.0f} s; total {cursor / 1000:.1f} s")

    guard = ReviewWriteGuard(context.store, context.review)
    def refuse_if_approved(text: str) -> None:
        guard.check(args[0], "captions.srt", text.encode())  # o gate 4 aprovado recusa a troca da legenda

    captions(episode_dir, episode_scenes, wavs, cursor, refuse_if_approved)
    word_captions(context, episode_dir, episode_scenes, scenes.language)
    episode = EpisodeManifest(
        schema_version=2, episode_id=scenes.episode_id, title=f"{scenes.episode_id} (rascunho)",
        language=scenes.language, format=EpisodeFormat.EXPLAINER, scenes=episode_scenes, host=scenes.host,
        series=scenes.series,
        video=VideoSpec.for_orientation(scenes.orientation), captions=CaptionsConstants.CAPTIONS,
    )
    if tracks := music(settings, episode_dir, episode):
        episode = EpisodeManifest.model_validate({**episode.model_dump(), "music": tracks})
        print(f"trilha: {len(tracks)} trecho(s), {len({m.asset_id for m in tracks})} faixa(s)")
    print("ritmo:", pacing_warnings(episode) or "ok")
    renderer = EpisodeRenderer(context.store, guard, context.renderer)
    if "--no-render" in sys.argv:
        renderer.assemble(args[0], scenes, episode)
        return
    started = time.monotonic()
    result = renderer.render(args[0], scenes, episode, preview="--preview" in sys.argv)
    print(f"render: {time.monotonic() - started:.0f} s -> {result.path} ({result.duration_ms / 1000:.1f} s)")
    if episode.music:
        lufs = integrated_lufs(result.path)
        problem = loudness_problem(lufs)
        print(f"volume: {lufs:.1f} LUFS", f"— alerta: {problem}" if problem else "ok")


if __name__ == "__main__":
    raise SystemExit(run("montar_episodio", main))
