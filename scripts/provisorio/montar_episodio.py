"""Voz e render de um episódio a partir do scenes.json (provisório até `vp voice` #16 e `vp render` #13).

Uso: `.venv/bin/python scripts/provisorio/montar_episodio.py <episode-id> [--no-render] [--preview]
     [--voz-final]`

- Narração por cena, em `voice/<cena>-<provedor>-<hash>.wav`: a voz dos rascunhos (`tts`, Kokoro) ou, com
  `--voz-final`, a do vídeo final (`tts_final`, Gemini Charon, ADR 012). O hash cobre o texto, o modelo, a voz
  e a direção de fala: a fala só é gerada de novo quando um deles muda, e uma voz não apaga as falas da outra.
- A voz final gera as cenas que faltam em lotes (várias cenas por chamada, cortadas nas pausas); lote que não
  pode ser cortado com segurança é gerado cena a cena. Cota esgotada: o script para, as falas já geradas ficam
  no cache e a próxima execução continua.
- Duração real de cada WAV (ffprobe) → tempo dos planos (app/pipeline/shots.py) → episode.json v2.
- Render pelo motor do formato explicativo (Remotion), com cache por cena.
- A mídia de cada plano de foto ou B-roll é `assets/<asset_id>.<ext>` (jpg, png, webp, mp4, webm).
- Com `sources.json` na pasta, cada plano com claims ganha a fonte do rodapé (ADR 011).
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

from app.bootstrap import build_context  # noqa: E402
from app.media.probe import duration_ms  # noqa: E402
from app.pipeline.schemas import (  # noqa: E402
    EpisodeFormat,
    EpisodeManifest,
    EpisodeScene,
    ScenesManifest,
    SourcesManifest,
    VideoSpec,
)
from app.pipeline.shots import episode_shots, pacing_warnings  # noqa: E402
from app.providers.errors import InvalidOutput, ProviderError  # noqa: E402
from app.providers.tts.base import SpeechRequest, TTSProvider  # noqa: E402
from app.render.remotion import RemotionEngine  # noqa: E402
from app.settings import Settings  # noqa: E402

MEDIA_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm")


BATCH_CHARS = 1200  # ~90 s de fala por chamada num lote da voz final (ADR 012)


def voice_fingerprint(settings: Settings, provider: str, language: str) -> str:
    """O que muda a fala gerada, além do texto: provedor, modelo, voz e direção de fala."""
    if provider == "gemini":
        gemini = settings.gemini_tts
        return f"gemini|{gemini.model}|{gemini.voices.get(language)}|{gemini.styles.get(language, '')}"
    return f"{provider}|{settings.kokoro.voices.get(language)}"


def batches(requests: list[SpeechRequest], limit: int = BATCH_CHARS) -> list[list[SpeechRequest]]:
    """Cenas seguidas em grupos de até `limit` caracteres (uma cena maior que o limite vai sozinha)."""
    groups: list[list[SpeechRequest]] = []
    size = 0
    for request in requests:
        if groups and size + len(request.text) <= limit:
            groups[-1].append(request)
            size += len(request.text)
        else:
            groups.append([request])
            size = len(request.text)
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
    provider = (settings.providers.tts_final or settings.providers.tts) if final else settings.providers.tts
    tts = context.tts_final if final else context.tts
    fingerprint = voice_fingerprint(settings, provider, scenes.language)
    voice_dir = episode_dir / "voice"
    voice_dir.mkdir(exist_ok=True)

    started = time.monotonic()
    wavs, missing = {}, []
    for scene in scenes.scenes:
        key = hashlib.sha256(f"{fingerprint}|{scene.narration}".encode()).hexdigest()[:10]
        wavs[scene.id] = wav = voice_dir / f"{scene.id}-{provider}-{key}.wav"
        if not wav.exists():
            for stale in voice_dir.glob(f"{scene.id}-{provider}-*.wav"):
                stale.unlink()
            missing.append(SpeechRequest(text=scene.narration, out_path=wav, language=scenes.language))
    if missing:
        generate(tts, missing)

    episode_scenes, cursor = [], 0
    for scene in scenes.scenes:
        wav = wavs[scene.id]
        ms = duration_ms(wav)
        shots = episode_shots(scene, ms, lambda shot: media_path(episode_dir, shot.asset_id), sources)
        episode_scenes.append(
            EpisodeScene(
                id=scene.id, start_ms=cursor, duration_ms=ms, narration=scene.narration,
                audio=f"voice/{wav.name}", shots=shots, host_corner=scene.host_corner,
            )
        )
        summary = ", ".join(f"{s.spec.kind} {s.duration_ms / 1000:.1f}" for s in shots)
        print(f"{scene.id}: {ms / 1000:5.2f} s | {summary}")
        cursor += ms
    print(f"voz: {time.monotonic() - started:.0f} s; total {cursor / 1000:.1f} s")

    episode = EpisodeManifest(
        schema_version=2, episode_id=scenes.episode_id, title=f"{scenes.episode_id} (rascunho)",
        language=scenes.language, format=EpisodeFormat.EXPLAINER, scenes=episode_scenes, host=scenes.host,
        video=VideoSpec.for_orientation(scenes.orientation),
    )
    (episode_dir / "episode.json").write_text(episode.model_dump_json(indent=2))
    print("ritmo:", pacing_warnings(episode) or "ok")
    if "--no-render" in sys.argv:
        return
    preview = "--preview" in sys.argv
    started = time.monotonic()
    out = episode_dir / "renders" / ("preview.mp4" if preview else "final.mp4")
    result = RemotionEngine().render(episode, episode_dir, out, preview=preview)
    print(f"render: {time.monotonic() - started:.0f} s -> {result.path} ({result.duration_ms / 1000:.1f} s)")


if __name__ == "__main__":
    main()
