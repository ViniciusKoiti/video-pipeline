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

import hashlib
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.bootstrap import LazyContext, build_context  # noqa: E402
from app.media.captions import (  # noqa: E402
    CAPTIONS,
    SceneAudio,
    captions_key,
    episode_cues,
    parse_srt,
    review_hints,
    sync_captions,
    timing_problems,
)
from app.media.loudness import integrated_lufs, loudness_problem  # noqa: E402
from app.media.narration import has_pauses, strip_pauses  # noqa: E402
from app.media.pauses import silences  # noqa: E402
from app.media.probe import duration_ms  # noqa: E402
from app.media.pronunciation import load_glossary, respell  # noqa: E402
from app.media.word_captions import WORDS, SceneSpeech, sync_words  # noqa: E402
from app.pipeline.music import load_music_catalog, resolve_music  # noqa: E402
from app.pipeline.schemas import (  # noqa: E402
    MUSIC_PLAN_FILE,
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
from app.providers.errors import InvalidOutput, ProviderError  # noqa: E402
from app.providers.tts.base import SpeechRequest, TTSProvider  # noqa: E402
from app.providers.tts.chatterbox import reference_hash  # noqa: E402
from app.render.remotion import RemotionEngine  # noqa: E402
from app.settings import Settings  # noqa: E402

MEDIA_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm")
MUSIC_SUFFIXES = (".mp3", ".m4a", ".wav", ".ogg")


# A voz clonada do dono: na máquina (ADR 016) ou numa GPU do Modal (ADR 024).
CLONED = ("chatterbox", "chatterbox_modal")
BATCH_CHARS = 1200  # ~90 s de fala por chamada num lote da voz final (ADR 012)


def voice_fingerprint(settings: Settings, provider: str, language: str) -> str:
    """O que muda a fala gerada, além do texto: provedor, modelo, voz e direção de fala."""
    if provider == "gemini":
        gemini = settings.gemini_tts
        return f"gemini|{gemini.model}|{gemini.voices.get(language)}|{gemini.styles.get(language, '')}"
    if provider in CLONED:  # a mesma voz local ou no Modal (ADR 024); o nome do WAV separa as duas
        box = settings.chatterbox
        reference = box.reference.expanduser() if box.reference else None
        voice = reference_hash(reference) if reference and reference.is_file() else None
        return f"{provider}|{box.model}|{box.language_ids.get(language)}|{voice}"
    return f"{provider}|{settings.kokoro.voices.get(language)}"


def batches(requests: list[SpeechRequest], limit: int = BATCH_CHARS) -> list[list[SpeechRequest]]:
    """Cenas seguidas em grupos de até `limit` caracteres (uma cena maior que o limite vai sozinha).
    Cena com `<short pause>` também vai sozinha: no teste de 2026-10-05 as pausas dentro da cena (até 1,1 s)
    não se destacaram da fronteira entre cenas, e o corte do lote foi recusado (ADR 015)."""
    groups: list[list[SpeechRequest]] = []
    size = 0
    open_group = False  # o último grupo ainda aceita mais cenas
    for request in requests:
        if has_pauses(request.text):
            groups.append([request])
            open_group = False
        elif open_group and size + len(request.text) <= limit:
            groups[-1].append(request)
            size += len(request.text)
        else:
            groups.append([request])
            size = len(request.text)
            open_group = True
    return groups


def generate(tts: TTSProvider, requests: list[SpeechRequest]) -> None:
    many = getattr(tts, "synthesize_many", None)
    groups = batches(requests) if many else [[r] for r in requests]
    print(f"voz: {len(requests)} cena(s) a gerar em {len(groups)} chamada(s)")
    for group in groups:
        try:
            if many and len(group) > 1:
                try:
                    many(group)
                    continue
                except InvalidOutput as error:
                    print(f"lote recusado ({error}); gerando cena a cena")
            for request in group:
                tts.synthesize_speech(request)
        except ProviderError as error:
            raise SystemExit(f"{group[0].out_path.name}: {error.reason}: {error}. As falas já geradas "
                             "ficam no cache; rode de novo depois.") from error


def media_path(episode_dir: Path, asset_id: str) -> str:
    for suffix in MEDIA_SUFFIXES:
        if (episode_dir / "assets" / f"{asset_id}{suffix}").is_file():
            return f"assets/{asset_id}{suffix}"
    raise SystemExit(f"ativo {asset_id} sem arquivo de mídia em assets/")


def music(settings: Settings, episode_dir: Path, episode: EpisodeManifest) -> list[EpisodeMusic]:
    """Trechos da trilha (ADR 030) com o tempo dos WAVs; sem `music.json`, nenhum."""
    plan_path = episode_dir / MUSIC_PLAN_FILE
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


def captions(episode_dir: Path, scenes: list[EpisodeScene], wavs: dict[str, Path], total_ms: int) -> None:
    """Gera ou mantém `captions.srt` e confere o arquivo que vai para o render (#17)."""
    audio = [
        SceneAudio(
            start_ms=scene.start_ms, duration_ms=scene.duration_ms, narration=scene.narration,
            silences_ms=[(round(a * 1000), round(b * 1000)) for a, b in silences(wavs[scene.id])],
        )
        for scene in scenes
    ]
    cues, approximate = episode_cues(audio)
    note = sync_captions(episode_dir, cues, captions_key([wavs[scene.id].name for scene in scenes]))
    found, problems = parse_srt((episode_dir / CAPTIONS).read_text())
    problems += timing_problems(found, total_ms)
    if problems:
        raise SystemExit(f"{CAPTIONS}: " + "; ".join(problems))
    print(f"legenda: {note}; {len(found)} blocos, {approximate} fronteira(s) no tempo proporcional")
    for n, hint in review_hints(found):
        print(f"  revisar bloco {n}: {hint}")


def word_captions(context: LazyContext, episode_dir: Path, scenes: list[EpisodeScene], language: str) -> None:
    """Palavras com tempo em `captions.words.json`; reconhece no Whisper remoto só com `--legenda-palavra`."""
    request = "--legenda-palavra" in sys.argv
    path = episode_dir / WORDS
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
                         f"ficam em {WORDS}; rode de novo depois.") from error
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
    if named:
        provider, tts = named, context.tts_named(named)
    else:
        choice = settings.providers
        provider = (choice.tts_final or choice.tts) if final else choice.tts
        tts = context.tts_final if final else context.tts
    fingerprint = voice_fingerprint(settings, provider, scenes.language)
    voice_dir = episode_dir / "voice"
    voice_dir.mkdir(exist_ok=True)
    glossary = load_glossary(episode_dir)

    started = time.monotonic()
    wavs, missing = {}, []
    for scene in scenes.scenes:
        # Cena com pausa: o silêncio do Kokoro entra na chave (ADR 015); sem pausa a chave não muda.
        pauses = {"kokoro": settings.kokoro.pause_ms, **dict.fromkeys(CLONED, settings.chatterbox.pause_ms)}
        pause_ms = pauses.get(provider)
        tagged = pause_ms is not None and has_pauses(scene.narration)
        pause = f"|pausa{pause_ms}" if tagged else ""
        # Entrega da fala (ADR 022): só a voz clonada obedece; a chave muda só quando a entrega não é neutra.
        delivery = scene.delivery or "neutral"
        entrega = f"|entrega:{delivery}" if provider in CLONED and delivery != "neutral" else ""
        text = respell(scene.narration, glossary)  # a grafia que a voz lê; sem termo, o texto do roteiro
        key = hashlib.sha256(f"{fingerprint}{pause}{entrega}|{text}".encode()).hexdigest()[:10]
        wavs[scene.id] = wav = voice_dir / f"{scene.id}-{provider}-{key}.wav"
        if not wav.exists():
            for stale in voice_dir.glob(f"{scene.id}-{provider}-*.wav"):
                stale.unlink()
            missing.append(
                SpeechRequest(text=text, out_path=wav, language=scenes.language, delivery=delivery)
            )
    if missing:
        generate(tts, missing)
    close = getattr(tts, "close", None)  # a voz clonada mantém um processo com o modelo carregado
    if close:
        close()

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

    captions(episode_dir, episode_scenes, wavs, cursor)
    word_captions(context, episode_dir, episode_scenes, scenes.language)
    episode = EpisodeManifest(
        schema_version=2, episode_id=scenes.episode_id, title=f"{scenes.episode_id} (rascunho)",
        language=scenes.language, format=EpisodeFormat.EXPLAINER, scenes=episode_scenes, host=scenes.host,
        series=scenes.series,
        video=VideoSpec.for_orientation(scenes.orientation), captions=CAPTIONS,
    )
    if tracks := music(settings, episode_dir, episode):
        episode = EpisodeManifest.model_validate({**episode.model_dump(), "music": tracks})
        print(f"trilha: {len(tracks)} trecho(s), {len({m.asset_id for m in tracks})} faixa(s)")
    (episode_dir / "episode.json").write_text(episode.model_dump_json(indent=2))
    print("ritmo:", pacing_warnings(episode) or "ok")
    if "--no-render" in sys.argv:
        return
    preview = "--preview" in sys.argv
    started = time.monotonic()
    out = episode_dir / "renders" / ("preview.mp4" if preview else "final.mp4")
    result = RemotionEngine().render(episode, episode_dir, out, preview=preview)
    print(f"render: {time.monotonic() - started:.0f} s -> {result.path} ({result.duration_ms / 1000:.1f} s)")
    if episode.music:
        lufs = integrated_lufs(result.path)
        problem = loudness_problem(lufs)
        print(f"volume: {lufs:.1f} LUFS", f"— alerta: {problem}" if problem else "ok")


if __name__ == "__main__":
    main()
